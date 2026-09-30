/* mapfix.asi - engine-level fix for pause-map zone labels showing wrong glyphs (target 3).

   ROOT CAUSE (proven by procdiag.asi capture): the pause-map zone-label path passes each
   character to CFont::ProcessString as (real codepoint - 0x20). ProcessString applies its
   own -0x20 internally and the CHS PrintCharDispatch adds +0x20 back, so the net codepoint
   used for the glyph lookup is (real - 0x20) -> wrong character. All 52 captured garbage
   strings equal a real zone name shifted by exactly -0x20 (52/52 recovered into the 74-zone
   table). Menu / POI labels / the current-zone readout pass REAL codepoints and render fine.

   FIX: hook ProcessString entry (GTAIV.exe RVA 0x5222A0, same 6-byte relocation-invariant
   patch as procdiag). At entry, if the incoming string EXACTLY equals one of the 74 known
   zone names shifted by -0x20, replace the str argument pointer with the DLL's read-only
   correct constant, then run the original ProcessString. Every other call passes through
   untouched. Zero drawing, whitelist-gated (exact full-string match), no game memory written.

   Safety: single entry hook; corrected string points to permanent DLL static data (no buffer
   lifetime issue); recursion-safe (the corrected real name never matches a -0x20 bad form).
   ASCII-only comments (MSVC decodes UTF-8 Chinese as GBK and swallows lines). */
#include <windows.h>
#include "zone_table.h"

#define PROCSTR_RVA   0x5222A0
#define PATCH_BYTES   6
#define MAXREAD       12          /* zone names are <= 9 chars; anything longer is not a zone */

static HMODULE g_self = 0, g_exe = 0;
static BYTE*   g_ps = 0;
static BYTE    g_saved[PATCH_BYTES];
static BYTE*   g_tramp = 0;
static HANDLE  g_log = INVALID_HANDLE_VALUE;
static long    g_installed = 0;
static volatile long g_fixes = 0;

static void wr(const char* s, int n){ DWORD w; if (g_log != INVALID_HANDLE_VALUE) WriteFile(g_log, s, (DWORD)n, &w, 0); }
static void wrs(const char* s){ wr(s, lstrlenA(s)); }
static void hex8(char* o, unsigned v){ const char* h="0123456789abcdef"; for (int i=0;i<8;i++) o[i]=h[(v>>(28-4*i))&15]; }

/* If str equals (some zone name with each char -0x20), return that zone's correct constant;
   otherwise return str unchanged. Reads str defensively; never writes game memory. */
static const unsigned short* __cdecl FixZone(const unsigned short* str){
  if (!str) return str;
  unsigned short buf[MAXREAD + 1];
  int n = 0;
  while (n < MAXREAD) {
    if (IsBadReadPtr((void*)(str + n), 2)) return str;   /* unreadable -> pass through */
    unsigned short c = str[n];
    buf[n] = c;
    if (c == 0) break;
    n++;
  }
  if (n == 0 || n >= MAXREAD) return str;                /* empty or too long -> not a zone label */
  if (buf[n] != 0) return str;                           /* not NUL-terminated within MAXREAD */

  for (int i = 0; i < ZONE_COUNT; i++) {
    if (ZONE_LEN[i] != n) continue;
    int match = 1;
    for (int k = 0; k < n; k++) {
      unsigned short want = (unsigned short)((ZONE_REAL[i][k] - 0x20) & 0xffff);
      if (buf[k] != want) { match = 0; break; }
    }
    if (match) {
      long c2 = InterlockedIncrement(&g_fixes);
      if (c2 <= 5 || (c2 % 500) == 0) { char b[48]; int j=0; b[j++]='f'; b[j++]='i'; b[j++]='x'; b[j++]=' '; hex8(b+j,(unsigned)c2); j+=8; b[j++]=' '; b[j++]='i'; b[j++]='d'; b[j++]='x'; b[j++]='='; hex8(b+j,(unsigned)i); j+=8; b[j++]='\r'; b[j++]='\n'; b[j]=0; wrs(b); }
      return ZONE_REAL[i];
    }
  }
  return str;
}

__declspec(naked) void __cdecl HookEntry(){
  __asm{
    push ebp
    mov  ebp, esp
    push dword ptr [ebp+0x10]    ; str arg
    call FixZone                 ; -> eax = corrected ptr (or original)
    add  esp, 4
    mov  dword ptr [ebp+0x10], eax ; swap str arg; original ProcessString reads corrected string
    pop  ebp
    jmp  [g_tramp]
  }
}

static bool install(){
  g_exe = GetModuleHandleA(NULL);
  if (!g_exe) { wrs("no exe base\r\n"); return false; }
  g_ps = (BYTE*)g_exe + PROCSTR_RVA;
  if (IsBadReadPtr((void*)g_ps, 16)) { wrs("ps unreadable\r\n"); return false; }
  static const BYTE expect6[PATCH_BYTES] = { 0x81,0xec,0x8c,0x0a,0x00,0x00 };
  for (int i = 0; i < PATCH_BYTES; i++) if (g_ps[i] != expect6[i]) { wrs("MISMATCH prologue\r\n"); return false; }
  for (int i = 0; i < PATCH_BYTES; i++) g_saved[i] = g_ps[i];
  g_tramp = (BYTE*)VirtualAlloc(0, 64, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
  if (!g_tramp) { wrs("tramp alloc fail\r\n"); return false; }
  for (int i = 0; i < PATCH_BYTES; i++) g_tramp[i] = g_saved[i];
  g_tramp[PATCH_BYTES] = 0xE9;
  *(DWORD*)(g_tramp + PATCH_BYTES + 1) = ((DWORD)g_ps + PATCH_BYTES) - ((DWORD)(g_tramp + PATCH_BYTES) + 5);
  DWORD old;
  if (!VirtualProtect(g_ps, PATCH_BYTES, PAGE_EXECUTE_READWRITE, &old)) { wrs("vprot fail\r\n"); return false; }
  g_ps[0] = 0xE9;
  *(DWORD*)(g_ps + 1) = (DWORD)HookEntry - ((DWORD)g_ps + 5);
  g_ps[5] = 0x90;
  VirtualProtect(g_ps, PATCH_BYTES, old, &old);
  FlushInstructionCache(GetCurrentProcess(), g_ps, PATCH_BYTES);
  return true;
}

static DWORD WINAPI Worker(LPVOID){
  char dir[MAX_PATH]; GetModuleFileNameA(g_self, dir, MAX_PATH);
  char* s = 0; for (char* p = dir; *p; p++) if (*p == '\\' || *p == '/') s = p;
  if (s) *(s + 1) = 0;
  char path[MAX_PATH]; lstrcpyA(path, dir); lstrcatA(path, "mapfix.log");
  g_log = CreateFileA(path, GENERIC_WRITE, FILE_SHARE_READ, 0, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, 0);
  wrs("mapfix start v1\r\n");
  for (int i = 0; i < 600 && !g_exe; i++){ g_exe = GetModuleHandleA(NULL); Sleep(50); }
  { char b[64]; int i=0; b[i++]='e'; b[i++]='x'; b[i++]='e'; b[i++]='='; hex8(b+i,(unsigned)(size_t)g_exe); i+=8; b[i++]='\r'; b[i++]='\n'; b[i]=0; wrs(b); }
  /* Do not patch ProcessString's prologue before GTA4.CHS.asi has resolved fnFont_ProcessString.
     CHS scans for the 81 EC 8C 0A 00 00 prologue synchronously inside its own DllMain; the ASI
     loader serializes DllMain calls, but the CHS module handle can become visible before its
     DllMain finishes. Wait for CHS, then a fixed margin, so either load order is safe. */
  for (int i = 0; i < 600 && !GetModuleHandleA("GTA4.CHS.asi"); i++) Sleep(100);
  Sleep(3000);
  if (InterlockedCompareExchange(&g_installed, 1, 0) != 0) return 0;
  if (install()) wrs("hook installed @ProcessString\r\n"); else wrs("hook FAILED\r\n");
  return 0;
}

BOOL WINAPI DllMain(HMODULE h, DWORD r, LPVOID){
  if (r == DLL_PROCESS_ATTACH){ g_self = h; DisableThreadLibraryCalls(h); CreateThread(0,0,Worker,0,0,0); }
  else if (r == DLL_PROCESS_DETACH){
    char b[48]; int j=0; b[j++]='t'; b[j++]='o'; b[j++]='t'; b[j++]='a'; b[j++]='l'; b[j++]='='; hex8(b+j,(unsigned)g_fixes); j+=8; b[j++]='\r'; b[j++]='\n'; b[j]=0; wrs(b);
    if (g_log != INVALID_HANDLE_VALUE){ FlushFileBuffers(g_log); CloseHandle(g_log); g_log = INVALID_HANDLE_VALUE; }
  }
  return TRUE;
}
