/* procdiag.asi - diagnostic hook on native CFont::ProcessString entry (GTAIV.exe RVA 0x5222A0).
   Goal: decide whether the pause-map zone labels flow through ProcessString at all,
   and if so, from which call site (return address) and with what coords / render state.
   Background: mapdiag (native PrintChar RVA 0x521140) saw ZERO CJK during pause map,
   and fontdiag-v2 (ASI PrintCharDispatch) saw ZERO map events. ProcessString is the
   layer ABOVE PrintChar and has never been instrumented. Note.txt of GTA4.CHS lists two
   UNHOOKED ProcessString call sites (VA 0x91C777, 0x922BA4) as author TODO.

   This DLL ONLY LOGS. It does not change any rendering. Single inline hook, zero draw.
   Deleting it (or leaving it .off) fully restores the game.

   ProcessString prologue:
     0x9222A0: 81 ec 8c 0a 00 00     sub  esp, 0xA8C          (6 bytes, NO address operand)
     0x9222A6: a1 b4 7f 05 01        mov  eax, [0x1057FB4]    (5 bytes, GS cookie; the operand
                                                                at RVA 0x5222A7 HAS a .reloc
                                                                HIGHLOW entry -> rewritten by ASLR)
   ASLR lesson (v1 failed here): GTAIV.exe rebases (runtime base seen 0x00E20000), so the
   cookie operand bytes differ at runtime and a disk-byte prologue check over 11 bytes fails.
   FIX: patch only the FIRST 6 bytes (sub esp,0xA8C) which contain no relocated operand, so the
   byte-check is runtime-valid; the cookie instruction is left in place and runs untouched.
   hook  = E9 rel32 + 1x 90 (6 bytes); trampoline = orig 6 bytes + E9 -> 0x9222A6.
   cdecl args at entry: [esp]=ret [esp+4]=posx [esp+8]=posy [esp+0C]=str [esp+10]=a4
   with (push ebp; mov ebp,esp): [ebp+4]=ret [ebp+8]=posx [ebp+0C]=posy [ebp+10]=str

   GTAChar = uint16 (UTF-16). CFontRenderState: nFont @ +0x29, TokenType @ +0x30.
   pFont_RenderState pointer lives at GTA4.CHS.asi + 0x5AE70 (same as mapdiag).
   NOTE: keep this file ASCII-only (UTF-8 Chinese comments get mis-decoded as GBK by cl). */
#include <windows.h>

#define PROCSTR_RVA   0x5222A0
#define PATCH_BYTES   6
#define RS_PTR_OFF    0x5ae70
#define TOK_OFF       0x30
#define NFONT_OFF     0x29
#define STR_MAX       32
#define STR_LOG       12
#define MAX_LINES     1500000

static HMODULE g_self = 0, g_exe = 0, g_chs = 0;
static BYTE*   g_ps = 0;
static BYTE    g_saved[PATCH_BYTES];
static BYTE*   g_tramp = 0;
static HANDLE  g_log = INVALID_HANDLE_VALUE;
static long    g_lines = 0, g_calls = 0, g_installed = 0, g_capped = 0;
static int     g_reentrant = 0;

static void wr(const char* s, int n){ DWORD w; if (g_log != INVALID_HANDLE_VALUE) WriteFile(g_log, s, (DWORD)n, &w, 0); }
static void wrs(const char* s){ wr(s, lstrlenA(s)); }
static void hex2(char* o, unsigned v){ const char* h="0123456789abcdef"; o[0]=h[(v>>4)&15]; o[1]=h[v&15]; }
static void hex4(char* o, unsigned v){ const char* h="0123456789abcdef"; o[0]=h[(v>>12)&15]; o[1]=h[(v>>8)&15]; o[2]=h[(v>>4)&15]; o[3]=h[v&15]; }
static void hex8(char* o, unsigned v){ const char* h="0123456789abcdef"; for (int i=0;i<8;i++) o[i]=h[(v>>(28-4*i))&15]; }
static void decu(char* o, unsigned v){ char t[12]; int n=0; if (v==0) t[n++]='0'; while (v){ t[n++]=(char)('0'+(v%10)); v/=10; } for (int i=0;i<n;i++) o[i]=t[n-1-i]; o[n]=0; }
static void logbytes(const char* tag, const BYTE* p, int n){
  char b[160]; int i=0;
  for (const char* q=tag; *q && i<40; q++) b[i++]=*q;
  for (int k=0;k<n && i<150;k++){ b[i++]=' '; hex2(b+i, p[k]); i+=2; }
  b[i++]='\r'; b[i++]='\n'; b[i]=0;
  wrs(b);
}

/* read up to STR_MAX wchars safely; returns count, fills out[] (<=STR_MAX), sets cjk if any >=0x80 */
static int readstr(const unsigned short* s, unsigned short* out, int* cjk){
  int n = 0; *cjk = 0;
  if (!s) return 0;
  while (n < STR_MAX) {
    if (IsBadReadPtr((void*)(s + n), 2)) break;
    unsigned short c = s[n];
    if (c == 0) break;
    out[n] = c; n++;
    if (c >= 0x80) *cjk = 1;
  }
  return n;
}

extern "C" void __cdecl ProcDiagLog(unsigned xbits, unsigned ybits, const unsigned short* str, unsigned ret){
  if (g_reentrant) return;
  g_reentrant = 1;

  unsigned short buf[STR_MAX]; int cjk = 0;
  int n = readstr(str, buf, &cjk);

  long total = ++g_calls;
  int doLog = cjk;
  if (!doLog && (total % 20000) == 0) doLog = 2;   /* heartbeat: proves hook alive even with no CJK */

  if (doLog && !g_capped) {
    if (g_lines >= MAX_LINES) { g_capped = 1; wrs("CAP_REACHED\r\n"); g_reentrant = 0; return; }

    /* render state (nFont / TokenType) from GTA4.CHS.asi global, guarded */
    unsigned nfont = 0xff, tok = 0xffffffff;
    if (g_chs && !IsBadReadPtr((void*)((BYTE*)g_chs + RS_PTR_OFF), 4)) {
      BYTE* rs = *(BYTE**)((BYTE*)g_chs + RS_PTR_OFF);
      if (rs && !IsBadReadPtr((void*)rs, 0x34)) { nfont = rs[NFONT_OFF]; tok = *(unsigned*)(rs + TOK_OFF); }
    }

    char b[200]; int i = 0;
    if (doLog == 2) { b[i++]='H'; b[i++]='B'; b[i++]=' '; }
    b[i++]='r'; b[i++]='='; hex8(b+i, ret); i+=8;
    b[i++]=' '; b[i++]='x'; b[i++]='='; hex8(b+i, xbits); i+=8;
    b[i++]=' '; b[i++]='y'; b[i++]='='; hex8(b+i, ybits); i+=8;
    b[i++]=' '; b[i++]='f'; b[i++]='='; hex2(b+i, nfont); i+=2;
    b[i++]=' '; b[i++]='t'; b[i++]='='; hex8(b+i, tok); i+=8;
    b[i++]=' '; b[i++]='n'; b[i++]='='; { char tmp[12]; decu(tmp, (unsigned)n); for (char* p=tmp; *p; p++) b[i++]=*p; }
    b[i++]=' '; b[i++]='s'; b[i++]='=';
    int sc = n < STR_LOG ? n : STR_LOG;
    for (int k = 0; k < sc && i < 190; k++){ b[i++]=' '; hex4(b+i, buf[k]); i+=4; }
    b[i++]='\r'; b[i++]='\n'; b[i]=0;
    wrs(b);
    if ((++g_lines % 512) == 0) FlushFileBuffers(g_log);
  }

  g_reentrant = 0;
}

__declspec(naked) void __cdecl HookEntry(){
  __asm{
    push ebp
    mov  ebp, esp
    ; cdecl: push args right-to-left for ProcDiagLog(xbits, ybits, str, ret)
    push dword ptr [ebp+0x04]    ; ret    (arg4, pushed 1st)
    push dword ptr [ebp+0x10]    ; str    (arg3, pushed 2nd)
    push dword ptr [ebp+0x0C]    ; posy   (arg2, pushed 3rd)
    push dword ptr [ebp+0x08]    ; posx   (arg1, pushed 4th/last)
    call ProcDiagLog
    add  esp, 16
    pop  ebp
    jmp  [g_tramp]
  }
}

static bool install(){
  g_exe = GetModuleHandleA(NULL);
  g_chs = GetModuleHandleA("GTA4.CHS.asi");
  if (!g_exe) { wrs("no exe base\r\n"); return false; }
  g_ps = (BYTE*)g_exe + PROCSTR_RVA;
  if (IsBadReadPtr((void*)g_ps, 16)) { wrs("ps unreadable\r\n"); return false; }
  logbytes("runtime bytes @ps:", g_ps, 12);
  /* verify only the relocation-invariant first instruction (sub esp,0xA8C) */
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
  char path[MAX_PATH]; lstrcpyA(path, dir); lstrcatA(path, "procdiag.log");
  g_log = CreateFileA(path, GENERIC_WRITE, FILE_SHARE_READ, 0, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, 0);
  wrs("procdiag start v2\r\n");
  for (int i = 0; i < 600 && !g_exe; i++){ g_exe = GetModuleHandleA(NULL); Sleep(50); }
  { char b[64]; int i=0; b[i++]='e'; b[i++]='x'; b[i++]='e'; b[i++]='='; hex8(b+i,(unsigned)(size_t)g_exe); i+=8; b[i++]='\r'; b[i++]='\n'; b[i]=0; wrs(b); }
  for (int i = 0; i < 600 && !g_chs; i++){ g_chs = GetModuleHandleA("GTA4.CHS.asi"); Sleep(100); }
  { char b[64]; int i=0; b[i++]='c'; b[i++]='h'; b[i++]='s'; b[i++]='='; hex8(b+i,(unsigned)(size_t)g_chs); i+=8; b[i++]='\r'; b[i++]='\n'; b[i]=0; wrs(b); }
  if (InterlockedCompareExchange(&g_installed, 1, 0) != 0) return 0;
  if (install()) wrs("hook installed @ProcessString\r\n"); else wrs("hook FAILED\r\n");
  return 0;
}

BOOL WINAPI DllMain(HMODULE h, DWORD r, LPVOID){
  if (r == DLL_PROCESS_ATTACH){ g_self = h; DisableThreadLibraryCalls(h); CreateThread(0,0,Worker,0,0,0); }
  else if (r == DLL_PROCESS_DETACH){ if (g_log != INVALID_HANDLE_VALUE){ FlushFileBuffers(g_log); CloseHandle(g_log); g_log = INVALID_HANDLE_VALUE; } }
  return TRUE;
}
