Решение:
1. fcrackzip -u -b -D -p rockyou.txt key.zip
   пароль будет: crisbrown2
2. Достали файл из архива
3. Далее steghide embed -ef flag.txt -cf kvnnrjmy\:nxkqzmtnzxmzo.rot
Если обратить внимание на rot, то намек на шифр Цезаря, нашли passphrase: scpverysecret
4. Получили флаг.