# -*- coding: utf-8 -*-

try:
    from requests import Session
except:
    print("[-] 'requests' Modülünüz yüklü değil yüklemek için; pip install requests")

try:
    from random import choice
except:
    print("[-] 'random' Modülünüz yüklü değil? Python indiridğinize emin misiniz? Yüklemek için; pip install requests")

from requests import Session
from random import choice

"""
Requestlerimizde kullanacağımız User-Agent'leri buraya koyuyorum.
Arasından rastgele bir tanesini seçip onu kullanacağım.
"""

USER_AGENTS = ["Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0",
"Mozilla/5.0 (Windows NT x.y; rv:10.0) Gecko/20100101 Firefox/10.0",
"Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0",
"Mozilla/5.0 (Windows NT x.y; WOW64; rv:10.0) Gecko/20100101 Firefox/10.0",
"Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/10.0",
"Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0",
"Mozilla/5.0 (Android; Mobile; rv:40.0) Gecko/40.0 Firefox/40.0"]


"""
Opener Sınıfı Argümanları:
    args:
        email: E-Posta adresi.
        full_name: Tam isim.
        username: Kullanıcı adı.
        password: Şifre.
        proxy: SSL Destekli HTTPS Proxy'si

Proxy Format Örneği: 1.1.1.1:8080

Eğer proxy'siz açmak istiyorsanız "proxy"
değerini "None" yapmalısınız.
"""

class Opener:
    def __init__(self,args):
        
        """
        Argümanların yeterliliğini onaylamak için "next_stage" isimli
        bir bool oluşturuyorum eğer sınıfa verilen argümanlar yetersiz
        ise "next_stage" değişkeni "False" olup hesap oluşturma bölümüne
        geçemeyecek.
        """

        self.next_stage = True

        if (args["email"] == None):
            print("[-] Lütfen bir e-posta giriniz!")
            self.next_stage = False
        if (args["username"] == None):
            print("[-] Lütfen bir kullanıcı adı giriniz!")
            self.next_stage = False
        if (args["full_name"] == None):
            print("[-] Lütfen bir tam isim giriniz!")
            self.next_stage = False
        if (args["password"] == None):
            print("[-] Lütfen bir şifre giriniz!")
            self.next_stage = False
        
        self.username = args["username"]
        self.full_name = args["full_name"]
        self.password = args["password"]
        self.email = args["email"]

        self.requestNumber = 0

        self.user_agent = choice(USER_AGENTS)

        self.ses = Session()

        ipcheck_response = self.ses.get("https://api.ipify.org?format=json")
        self.normalip = ipcheck_response.json()["ip"]

        if (args["proxy"] != None):
            self.proxy = args["proxy"]
            self.ses.proxies.update({
                "https":"https://" + self.proxy,
            })
            try:
                ipcheck_response = self.ses.get("https://api.ipify.org?format=json")
                proxyip = ipcheck_response.json()["ip"]
                if (proxyip == self.normalip):
                    self.next_stage = False
            except Exception as e:
                self.next_stage = False


        if (self.next_stage == False):
            self.ses.close()
    
    def UpdateHeaders(self):
        """
        Session'umuzda kullanacağımız headerleri tek tek
        ayarlamak yerine direk bu fonksiyon ile ayarlamak
        istedim.

        Bu headerleri nerden buldum derseniz öncelikle instagram'a
        yeni bir hesap ile kayıt oldum ve gelen requestleri inceledim
        bunu siz de Öğeyi denetle'den Network veya Ağ yazan yerde inceleye-
        bilirsiniz.

        Header'leri yazarken dikkat etmelisiniz tek yazım hatası yaptığınız
        request'leri bozabilir.

        Content-Length ve Cookie gibi gerekli olmayan header'leri
        koymak zorunda değilsiniz. Cookie önemli gibi görünebilir
        ama zaten Cookie'lerimize kolayca erişebiliyorlar.

        Buradaki çoğu header'in ne anlama geldiğini Mozilla'nın sitesinden
        bakabilirsiniz.

        X-Instagram-AJAX Yapılan requestlerin sayısıyla ilgili bir şey
        galiba o yüzden hep sayıyı hep aynı tutmak istemiyorum.
        """

        self.requestNumber = self.requestNumber + 1

        headers = {
            "Accept":"*/*",
            "Accept-Encoding":"gzip,deflate,br",
            "Accept-Language":"en-US,en;q=0.5",
            "Connection":"keep-alive",
            "Content-Type":"application/x-www-form-urlencoded",
            "DNT":"1",
            "Host":"www.instagram.com",
            "Referer":"https://www.instagram.com/accounts/emailsignup/",
            "TE":"Trailers",
            "User-Agent":self.user_agent,
            "X-CSRFToken":self.ses.cookies.get_dict()["csrftoken"],
            "X-Instagram-AJAX":str(self.requestNumber),
            "X-Requested-With":"XMLHttpRequest"
        }

        self.ses.headers.update(headers)

    def GETAndUpdate(self,url):
        """
        Normal bir GET requestinden bir farkı yok sadece
        geri donüş kodu 200 ise yani request başarılı ise
        çerezleri güncelliyor.
        """
        response = self.ses.get(url)
        if (response.status_code == 200):
            self.ses.cookies.update(response.cookies)
        return response

    def POSTAndUpdate(self,url,data):
        """
        GETAndUpdate fonksiyonuyla aynı sadece POST requesti
        yolluyor.
        """

        response = self.ses.post(url,data=data)
        if (response.status_code == 200):
            self.ses.cookies.update(response.cookies)
        return response

    def Register(self):
        """
        Register fonksiyonunun dönüş formatı:
        {
            "status": "False" veya "True",
            "message": "Hata mesajı." veya "None"
        }
        """

        if (self.next_stage == False):
            return {
                "status":False,
                "message":"Verilen argumanlarda eksiklik var veya Proxy bozuk"
            }
        
        # Bu yaptığımız request Cookie'leri almak ve Header'leri yüklemek içindi.
        self.GETAndUpdate("https://www.instagram.com/accounts/emailsignup/")
        self.UpdateHeaders()
        # Bu yaptığımız request hani username yazarız bu kullanılıyor vs der onu denemek için.
        web_create_response = self.POSTAndUpdate("https://www.instagram.com/accounts/web_create_ajax/attempt/",{
            "email":self.email,
            "first_name":self.full_name,
            "opt_into_one_tap":"false", # Bunun ne olduğunu bende bilmiyorum ama gerekli galiba :D
            "password":self.password,
            "username":self.username
        })
        # Şimdi yaptığımız request başarılı mı diye bakacağız.
        if (web_create_response.status_code == 200 and web_create_response.json()["dryrun_passed"] == True):
            # Tamamdır şimdi asıl kayıt olma requestine giriyoruz.
            register_response = self.POSTAndUpdate("https://www.instagram.com/accounts/web_create_ajax/",{
                "email":self.email,
                "first_name":self.full_name.replace(" ","+"),
                "opt_into_one_tap":"false", # Bunun ne olduğunu bende bilmiyorum ama gerekli galiba :D
                "password":self.password,
                "seamless_login_enabled":"1",
                "tos_version":"row",
                "username":self.username
            })
            if (register_response.status_code == 200 and register_response.json()["account_created"] == True):
                return {
                    "status":True,
                    "message":None
                }
            else:
                return {
                    "status":False,
                    "message":register_response.text
                }
        else:
            return {
                "status":False,
                "message":web_create_response.text
            }

"""
Profil oluşturmak için bir sitenin API'sini kullanıyorum.
http://rp.burakgarci.net/#api

E-Mail içinse bir 10 dakikalık E-Mail adresi kullanıyorum.
https://10minutemail.net/address.api.php?new=1
"""

class Profile:
    def __init__(self):
        self.ses = Session()
        self.response = None

    def Generate(self):
        response = self.ses.get("http://rp.burakgarci.net/api.php")
        if (response.status_code == 200):
            self.response = response
            return response.json()
        else:
            return None
    
    def GenerateUserName(self):
        if (self.response != None):
            names = self.response.json()["tam_isim"].split(" ")
            username = self.response.json()["kullanici_adi"] + "_" + str(choice(range(100)))
            return username
        else:
            return None

    def GenerateMail(self):
        if (self.response != None):
            response = self.ses.get("https://10minutemail.net/address.api.php?new=1")
            if (response.status_code == 200):
                return response.json()["mail_get_mail"]
            else:
                return None

    profilegenerator = Profile()
    info = profilegenerator.Generate()
    account_opener = Opener({
        "email":profilegenerator.GenerateMail(),
        "full_name": info["tam_isim"],
        "username": profilegenerator.GenerateUserName(),
        "password":"XHO7abrjxW",
        "proxy": "36.89.75.225:36940/"
    })
    print(account_opener.Register())