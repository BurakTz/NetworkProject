# Chat Sistemi (Python + Socket + SQLite)

Bu proje, TCP/IP soketleriyle çalışan, kullanıcıların kayıt olup giriş yapabildiği ve hem genel hem de özel sohbet gerçekleştirebildiği bir **sohbet uygulamasıdır**. Veriler, kalıcı olarak SQLite veritabanında tutulur.

## Özellikler

* Kullanıcı kaydı (`REGISTER`) ve girişi (`LOGIN`)
* Genel sohbet (herkese açık mesaj gönderme) (`SEND`)
* Özel sohbet isteği gönderme ve kabul etme (`REQUEST`, `ACCEPT`)
* Onaylı kullanıcılarla özel sohbet başlatma (`OPEN CHAT`)
* Özel mesaj gönderme (`PRIVATE SEND`)
* Geçmiş özel mesajları görme
* Kullanıcıların online / offline durumunu listeleme (`WHO`, `CHAT DURUM YENILE`)
* Özel sohbet kapatma (`CLOSE CHAT`)
* Oturumu kapatma veya sistemden çıkma (`DISCONNECT`, `EXIT`)
* SQLite veritabanı ile kalıcı mesaj saklama

## Dosyalar

| Dosya Adı       | Açıklama                                                   |
| --------------- | ---------------------------------------------------------- |
| `server.py`     | Tüm istemcileri yöneten ve komutları işleyen sunucu        |
| `client.py`     | Kullanıcının terminal üzerinden bağlandığı istemci arayüzü |
| `db_handler.py` | Veritabanı işlemlerini yöneten yardımcı modül              |
| `create_db.py`  | SQLite veritabanını ve gerekli tabloları oluşturur         |
| `reset_data.py` | (İsteğe bağlı) Veritabanını ve kayıtlı verileri sıfırlar   |
| `chat.db`       | SQLite veritabanı dosyası (otomatik oluşur)                |

## Sunucunun Çalıştırılması

Sunucuyu başlatmak için aşağıdaki adımları takip et:

### 1. Proje Klasörüne Gir

Terminali aç ve projenin bulunduğu klasöre geç:

```bash
cd proje-klasoru-adi
```

### 2. Veritabanını Oluştur

Veritabanı ve tabloların oluşturulması için sadece bir kereye mahsus aşağıdaki komutu çalıştır:

```bash
python create_db.py
```

Bu işlem sonunda `chat.db` dosyası otomatik olarak oluşur.

### 3. Sunucuyu Başlat

Sunucuyu başlatmak için aşağıdaki komutu gir:

```bash
python server.py
```

Başarılı bir şekilde başlatıldığında ekrana şu mesaj gelir:

```
[Sunucu başlatıldı] Dinleniyor...
```

Artık istemciler bağlanabilir ve mesajlaşma başlayabilir.

## Komutlar

### 1. Kayıt ve Giriş

```bash
REGISTER burak 1234          # Yeni kullanıcı oluşturur
LOGIN burak 1234             # Sisteme giriş yapar
```

### 2. Genel Sohbet

```bash
SEND Merhaba herkese!        # Genel sohbete mesaj gönderir
WHO                          # Şu anda çevrimiçi olan kullanıcıları listeler
```

### 3. Özel Sohbet İşlemleri

```bash
REQUEST ahmet                # 'ahmet' kullanıcısına özel sohbet isteği gönderir
ACCEPT burak                 # 'burak' kullanıcısından gelen isteği kabul eder
OPEN CHAT ahmet              # Onaylı kullanıcı ile özel sohbeti başlatır
PRIVATE SEND selam nasılsın  # Özel sohbette mesaj gönderir
CLOSE CHAT                   # Açık olan özel sohbeti kapatır
```

### 4. Sohbet Durumu ve Çıkış

```bash
CHAT DURUM YENILE            # Önceden konuşulan kişilerin anlık durumunu listeler
DISCONNECT                   # Oturumdan çıkar ama bağlantıyı kapatmaz
EXIT                         # Tamamen çıkış yapar ve bağlantıyı kapatır
```

## Notlar

* Tüm mesajlar SQLite veritabanına kaydedilir. Kullanıcı offline olsa bile geçmişe erişebilirsiniz.
* Sadece karşılıklı ACCEPT yapıldıktan sonra özel sohbet başlatılabilir.
* Her kullanıcı kendi istemcisinden komutları yazarak sohbeti yönetir.
