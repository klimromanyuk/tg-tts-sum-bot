import sys, os, time, socket, ssl, platform, asyncio, traceback, urllib.request

HOST = "speech.platform.bing.com"
PORT = 443
TEST_URL = f"https://{HOST}/"
CONTROL_URL = "https://www.bing.com/"
TEST_TEXT = "Проверка Edge TTS. Раз, два, три."
TEST_VOICE = "ru-RU-DmitryNeural"

def hr(title=""):
    print("\n" + "="*60)
    if title:
        print(title)
        print("-"*60)

def env_proxy_dump():
    keys = ["HTTP_PROXY","HTTPS_PROXY","ALL_PROXY","NO_PROXY","http_proxy","https_proxy","all_proxy","no_proxy"]
    found = False
    for k in keys:
        v = os.environ.get(k)
        if v:
            found = True
            print(f"{k} = {v}")
    if not found:
        print("Proxy env: (не найдено)")

def dns_check(host):
    hr("1) DNS")
    try:
        infos = socket.getaddrinfo(host, None)
        ips = sorted({i[4][0] for i in infos})
        print(f"OK: {host} -> {', '.join(ips[:10])}" + ("" if len(ips)<=10 else f" ... (+{len(ips)-10})"))
        return True
    except Exception as e:
        print(f"FAIL: DNS не резолвится: {e}")
        return False

def tcp_check(host, port, timeout=5):
    hr("2) TCP connect 443")
    try:
        t0 = time.time()
        with socket.create_connection((host, port), timeout=timeout) as s:
            dt = (time.time() - t0) * 1000
            print(f"OK: TCP подключение установлено за {dt:.0f} ms")
        return True
    except Exception as e:
        print(f"FAIL: TCP не подключается: {repr(e)}")
        return False

def tls_https_check(url, timeout=8):
    hr("3) HTTPS/TLS request")
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent":"Mozilla/5.0"})
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            code = resp.getcode()
            server = resp.headers.get("Server")
            print(f"OK: HTTP {code}, Server={server}")
            return True
    except Exception as e:
        print("FAIL: HTTPS/TLS запрос не прошёл.")
        print(f"Error: {repr(e)}")
        return False

async def edge_list_voices():
    import edge_tts
    # В edge-tts есть VoicesManager
    vm = await edge_tts.VoicesManager.create()
    voices = vm.voices
    return voices

async def edge_synthesize(text, voice):
    import edge_tts
    com = edge_tts.Communicate(text=text, voice=voice)
    total = 0
    async for chunk in com.stream():
        if chunk.get("type") == "audio":
            total += len(chunk.get("data", b""))
    return total

async def edge_tests():
    hr("4) edge-tts tests")
    try:
        import importlib.metadata as m
        ver = m.version("edge-tts")
        print(f"edge-tts version: {ver}")
    except Exception as e:
        print(f"edge-tts version: (не смог определить) {e}")

    try:
        voices = await edge_list_voices()
        print(f"OK: voices count = {len(voices)}")
        # покажем несколько русских голосов, если есть
        ru = [v for v in voices if v.get("Locale","").startswith("ru-")]
        print(f"RU voices found: {len(ru)}")
        if ru[:6]:
            for v in ru[:6]:
                print(f"- {v.get('ShortName')} | {v.get('Gender')} | {v.get('FriendlyName')}")
    except Exception as e:
        print("FAIL: не смог получить список голосов через edge-tts.")
        print(f"Error: {repr(e)}")
        print(traceback.format_exc())

    try:
        total = await edge_synthesize(TEST_TEXT, TEST_VOICE)
        if total > 0:
            print(f"OK: synth audio bytes = {total} (voice={TEST_VOICE})")
        else:
            print(f"FAIL: synth вернул 0 bytes (voice={TEST_VOICE})")
    except Exception as e:
        print("FAIL: синтез не сработал.")
        print(f"Error: {repr(e)}")
        print(traceback.format_exc())

def main():
    hr("SYSTEM")
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"OpenSSL: {ssl.OPENSSL_VERSION}")
    env_proxy_dump()

    dns_ok = dns_check(HOST)
    tcp_ok = tcp_check(HOST, PORT) if dns_ok else False

    # Проверка TLS/HTTPS на целевом и на контрольном домене
    tls_target_ok = tls_https_check(TEST_URL) if dns_ok else False
    tls_control_ok = tls_https_check(CONTROL_URL)

    # edge-tts тесты
    try:
        asyncio.run(edge_tests())
    except Exception as e:
        hr("edge-tts async runner FAIL")
        print(repr(e))
        print(traceback.format_exc())

    hr("SUMMARY")
    print(f"DNS({HOST}) = {dns_ok}")
    print(f"TCP({HOST}:443) = {tcp_ok}")
    print(f"HTTPS({TEST_URL}) = {tls_target_ok}")
    print(f"HTTPS({CONTROL_URL}) = {tls_control_ok}")
    print("\nЕсли DNS/TCP/HTTPS к speech.platform.bing.com FAIL, то это почти наверняка блокировка/провайдер/фаервол.")
    print("Если DNS/TCP/HTTPS OK, но edge-tts FAIL — вероятна блокировка WebSocket или частичная фильтрация трафика.")

if __name__ == "__main__":
    main()