import socket
import smtplib

# Test de connectivité réseau
def test_port(host, port):
    try:
        print(f"🔍 Test de connexion à {host}:{port}...")
        socket.create_connection((host, port), timeout=10)
        print(f"✅ Port {port} accessible")
        return True
    except Exception as e:
        print(f"❌ Port {port} bloqué: {e}")
        return False

# Test des 2 ports Gmail
print("=" * 50)
print("TEST DE CONNECTIVITÉ GMAIL")
print("=" * 50)

port_465 = test_port("smtp.gmail.com", 465)
port_587 = test_port("smtp.gmail.com", 587)

print("\n" + "=" * 50)
print("RÉSULTATS")
print("=" * 50)

if not port_465 and not port_587:
    print("❌ Aucun port SMTP accessible")
    print("Causes possibles:")
    print("  - Firewall bloquant les connexions SMTP")
    print("  - Antivirus interférant")
    print("  - Proxy/VPN actif")
    print("  - FAI bloquant les ports SMTP")
elif port_587:
    print("✅ Utilisez le port 587 (recommandé)")
elif port_465:
    print("✅ Utilisez le port 465")