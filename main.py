from databasefunction.db_handler import add_user, check_login, update_status, logout_user, update_status
import sys

def main_menu():
    current_user = None

    while True:
        print("\n Ana Menü")
        print("1 - Kayıt Ol")
        print("2 - Giriş Yap")
        print("3 - Çıkış Yap")
        print("4 - Durum Değiştir (Online)")
        print("5 - Durum Değiştir (Offline)")
        print("0 - Programdan Çık\n")

        choice = input("Seçimin: ").strip()

        if choice == "1":
            nickname = input("Kullanıcı adı: ")
            password = input("Şifre: ")
            success = add_user(nickname, password)
            print("Kayıt başarılı!" if success else " Bu kullanıcı adı zaten alınmış.")

        elif choice == "2":
            if current_user:
                print("⚠Zaten giriş yapılmış.")
                continue
            nickname = input("Kullanıcı adı: ")
            password = input("Şifre: ")
            user = check_login(nickname, password)
            if user:
                update_status(user[0], "online")
                current_user = user
                print(f"Giriş başarılı! Hoş geldin, {nickname}")
            else:
                print("Giriş başarısız. Kullanıcı adı veya şifre hatalı.")

        elif choice == "3":
            if not current_user:
                print("⚠Henüz giriş yapılmamış.")
                continue
            logout_user(current_user[1])
            print(f"{current_user[1]} çıkış yaptı.")
            current_user = None

        elif choice == "4":
            if not current_user:
                print("⚠Önce giriş yapmalısın.")
                continue
            update_status(current_user[0],"online")  # user_id

        elif choice == "5":
            if not current_user:
                print("⚠Önce giriş yapmalısın.")
                continue
            update_status(current_user[0],"offline")  # user_id

        elif choice == "0":
            print("Görüşmek üzere!")
            sys.exit()

        else:
            print("Geçersiz seçim.")

if __name__ == "__main__":
    main_menu()
