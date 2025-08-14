# SpongeBob Crypto TCP (Railway)

## محلياً
# اختياري: جرّب socat محلياً بنفس الفكرة
# لازم يكون socat مثبت عندك
export PORT=9000
socat TCP-LISTEN:$PORT,fork,reuseaddr EXEC:"python server.py",pty,setsid,ctty

# افتح اتصال:
nc 127.0.0.1 9000

## على Railway
1) ادفع الريبو إلى GitHub.
2) من Railway: New Project → Deploy from GitHub.
3) بعد الديبولوي، فعّل **TCP Proxy** من: Service → Settings → Networking → TCP Proxy (اختَر البورت الداخلي = $PORT).
4) اختبر:
nc <TCP_HOST> <TCP_PORT>
