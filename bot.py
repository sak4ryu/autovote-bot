import time
import sys
import os
import subprocess
import re
from datetime import datetime, timedelta

# Fix pour Python 3.13
try:
    import distutils
except ImportError:
    import setuptools

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.action_chains import ActionChains

# --- GESTION DE L'AFFICHAGE FANTÔME ---
HAS_DISPLAY_LIB = False
try:
    if sys.platform.startswith('linux'):
        from pyvirtualdisplay import Display
        HAS_DISPLAY_LIB = True
except ImportError:
    pass

# --- SYSTÈME DE LOGS (NOUVEAU) ---
def log(message):
    """
    Affiche le message dans la console ET l'écrit dans un fichier texte.
    Nettoie les codes couleurs pour le fichier texte.
    """
    # 1. Affichage Console (avec couleurs)
    print(message)
    
    # 2. Nettoyage des codes couleurs ANSI pour le fichier log
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    message_propre = ansi_escape.sub('', message)
    
    # 3. Écriture dans le fichier avec Timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open("journal_bot.txt", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message_propre}\n")
    except Exception as e:
        print(f"⚠️ Impossible d'écrire dans le log : {e}")

# --- FONCTIONS UTILITAIRES ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def afficher_banniere():
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    banniere = f"""
{CYAN}    _         _          {MAGENTA} _   _       _       
{CYAN}   / \  _   _| |_ ___    {MAGENTA}| | | | ___ | |_ ___ 
{CYAN}  / _ \| | | | __/ _ \   {MAGENTA}| | | |/ _ \| __/ _ \\
{CYAN} / ___ \ |_| | || (_) |  {MAGENTA}\ \_/ / (_) | ||  __/
{CYAN}/_/   \_\__,_|\__\___/   {MAGENTA} \___/ \___/ \__\___|{RESET}
    """
    print(banniere)
    print(f"{BOLD}{YELLOW}        >>> by sak4ryu <<<{RESET}")
    print(f"{GREEN}   -----------------------------------{RESET}")

def changer_ip(methode):
    log("\n🔄 -----------------------------------")
    if methode == "1": # MANUEL
        log("⚠️  ACTION REQUISE : Changement d'IP manuel")
        for _ in range(3):
            print('\a')
            time.sleep(0.5)
        print("👉 1. Mode Avion ON.")
        print("👉 2. Mode Avion OFF.")
        print("👉 3. Attendre la 4G.")
        input("⌨️  Appuie sur [ENTRÉE] quand c'est fait...")
        log("✅ Reprise après changement IP...")
    elif methode == "2": # VPN
        try:
            log("🌍 Changement VPN (Auto)...")
            cmd = "nordvpn connect" if sys.platform.startswith('linux') else "nordvpn -c"
            os.system(cmd) 
            time.sleep(10)
            log("✅ VPN reconnecté.")
        except:
            log("❌ Erreur commande VPN.")
    log("🔄 -----------------------------------\n")

def attendre_prochain_cycle(secondes_attente):
    maintenant = datetime.now()
    prochain_run = maintenant + timedelta(seconds=secondes_attente)
    heures = int(secondes_attente // 3600)
    minutes = int((secondes_attente % 3600) // 60)
    
    log(f"\n💤 \033[96mMode Veille Activé.\033[0m")
    log(f"⏱️  Attente : {heures}h {minutes}m")
    log(f"⏰ Réveil prévu à : \033[93m{prochain_run.strftime('%H:%M:%S')}\033[0m")
    
    try:
        time.sleep(secondes_attente)
    except KeyboardInterrupt:
        log("\n🛑 Arrêt manuel pendant la veille.")
        sys.exit()
        
    log("\n🔔 RÉVEIL DU BOT !")
    for _ in range(5):
        print('\a')
        time.sleep(0.2)

def extraire_temps_attente(texte):
    try:
        match_h = re.search(r'(\d+)h', texte)
        h = int(match_h.group(1)) if match_h else 0
        match_m = re.search(r'(\d+)m', texte)
        m = int(match_m.group(1)) if match_m else 0
        return (h * 3600) + (m * 60) + 90 
    except:
        return 3 * 3600 + 120

# --- FONCTION CŒUR ---
def lancer_vote(pseudo_cible, choix_recompense, mode_discret=False):
    URL_VOTE = "https://www.pactify.fr/votes"
    TEXTE_DU_LIEN = "Clique ici pour continuer..." 
    TEMPS_STANDARD = 3 * 3600 + 120
    
    log(f"\n🚀 Lancement pour : \033[96m{pseudo_cible}\033[0m")

    display = None
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    
    if mode_discret:
        if sys.platform.startswith('linux'):
            if HAS_DISPLAY_LIB:
                log("👻 Mode Fantôme Linux (Xvfb) activé.")
                display = Display(visible=0, size=(1920, 1080))
                display.start()
            else:
                log("⚠️  'pyvirtualdisplay' manquant. Navigateur visible.")
        elif sys.platform.startswith('win'):
            log("👻 Mode Fantôme Windows (Hors Champ) activé.")
            options.add_argument("--window-position=-3000,0")
    
    driver = uc.Chrome(options=options)

    try:
        log(f"Connexion à {URL_VOTE}...")
        driver.get(URL_VOTE)
        wait = WebDriverWait(driver, 20)

        wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
        username_input = wait.until(EC.visibility_of_element_located((By.NAME, "name")))
        username_input.clear()
        username_input.send_keys(pseudo_cible)
        
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Continuer')]"))).click()
        time.sleep(2) 
        
        # Check Erreurs
        try:
            wait_short = WebDriverWait(driver, 2)
            wait_short.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Aucun joueur')]")))
            log(f"\n\033[91m⛔ Pseudo invalide ou inexistant.\033[0m")
            return TEMPS_STANDARD 
        except: pass

        # Check Timer
        try:
            wait_short = WebDriverWait(driver, 2)
            timer_btn = wait_short.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Patient')]")))
            t_attente = extraire_temps_attente(timer_btn.text)
            log(f"\n\033[91m⛔ Déjà voté. Calcul attente : {int(t_attente/60)}min\033[0m")
            return t_attente
        except:
            log("✅ Vote disponible.")

        wait.until(EC.element_to_be_clickable((By.XPATH,"//*[contains(text(), 'Voter')]"))).click()
        driver.switch_to.default_content()
        time.sleep(5) 

        log("🕵️  Passage Cloudflare...")
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
        
        for i in range(5): 
            try: driver.find_element(By.TAG_NAME, "body").click()
            except: pass
            ActionChains(driver).send_keys(Keys.TAB).perform()
            time.sleep(0.2)
            ActionChains(driver).send_keys(Keys.SPACE).perform()
            time.sleep(3)
            if "instant" not in driver.title.lower():
                log("✅ Cloudflare passé.")
                break
        
        log("⏳ Chargement Captcha (20s)...")
        time.sleep(20) 

        try:
            lien = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(), '{TEXTE_DU_LIEN}')]")))
            lien.click()
            log("✅ Lien intermédiaire cliqué.")
        except:
            log("⚠️ Lien non trouvé (peut-être déjà passé).")
        
        time.sleep(5)
        
        log("🥊 Validation Captcha final...")
        try:
            driver.find_element(By.TAG_NAME, "body").click()
            time.sleep(1)
            ActionChains(driver).send_keys(Keys.TAB).pause(0.5).send_keys(Keys.TAB).pause(0.5).send_keys(Keys.SPACE).perform()
            log("✅ Combo touches envoyé.")
        except: pass

        time.sleep(10)

        try:
            l = driver.find_elements(By.XPATH, "//*[contains(text(), 'Voter')]")
            if l: l[0].click()
        except: pass

        log("🎁 Récupération récompense...")
        driver.close() 
        driver.switch_to.window(driver.window_handles[0]) 
        driver.switch_to.default_content()
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))

        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Recevoir ma récompense')]"))).click()
            time.sleep(2)
            if choix_recompense == "1":
                wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Objets')]"))).click()
                log(f"\033[92m✅ OBJETS RÉCUPÉRÉS POUR {pseudo_cible} !\033[0m")
            else:
                wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'VIP')]"))).click()
                log(f"\033[92m✅ POINTS VIP RÉCUPÉRÉS POUR {pseudo_cible} !\033[0m")
        except:
            log(f"❌ Erreur click récompense.")

        time.sleep(3)
        return TEMPS_STANDARD

    except Exception as e:
        log(f"❌ Erreur Technique : {e}")
        return TEMPS_STANDARD

    finally:
        driver.quit()
        if display: display.stop()

# --- MAIN ---
clear_screen()
afficher_banniere()

# On initialise le log de session
log("=== NOUVELLE SESSION DU BOT DÉMARRÉE ===")

try:
    print("\n\033[93m[?] Mode Discret (Navigateur caché) ?\033[0m")
    print("    1 - Oui")
    print("    2 - Non")
    rep_discret = input("\033[96m    Votre choix > \033[0m").strip()
    EST_DISCRET = (rep_discret == "1")

    print("\n\033[93m[?] Mode de fonctionnement :\033[0m")
    print("    1 - Farming Unique (Boucle 3h)")
    print("    2 - Mode Bulk (Liste)")
    mode = input("\033[96m    Votre choix > \033[0m").strip()

    print("\n\033[93m[?] Récompense ?\033[0m")
    print("    1 - Objets")
    print("    2 - VIP")
    choix_rec = input("\033[96m    Votre choix > \033[0m").strip()

    # --- EXECUTION ---
    if mode == "1":
        pseudo = input(f"\n[?] Pseudo : ").strip() or "msk_ocho"
        
        print("\n\033[93m[?] IP Reset manuel (iPhone) ?\033[0m")
        ip_choice = input("    1-Oui  2-Non > ").strip()
        
        if ip_choice == "1":
            print("\n[?] Reset IP maintenant (avant de commencer) ? (o/n)")
            if input(" > ").lower() == 'o': changer_ip("1")

        cycle = 1
        while True:
            clear_screen()
            afficher_banniere()
            log(f"\n🔄 CYCLE {cycle} - {datetime.now().strftime('%H:%M')}")
            
            t_wait = lancer_vote(pseudo, choix_rec, mode_discret=EST_DISCRET)
            
            cycle += 1
            attendre_prochain_cycle(t_wait)
            if ip_choice == "1": changer_ip("1")

    elif mode == "2":
        print("\n[?] Reset IP entre chaque vote ?")
        print("    1-iPhone  2-VPN  3-Non")
        ip_mode = input(" > ").strip()

        if not os.path.exists("pseudos.txt"): 
            log("❌ Pas de pseudos.txt")
            sys.exit()
            
        with open("pseudos.txt") as f: lst = [l.strip() for l in f if l.strip()]
        
        for i, p in enumerate(lst):
            log(f"\n--- Joueur {i+1}/{len(lst)} ---")
            if ip_mode in ["1","2"]: changer_ip(ip_mode)
            
            lancer_vote(p, choix_rec, mode_discret=EST_DISCRET)
            time.sleep(5)
            
    log("\n👋 Fin du script.")

except KeyboardInterrupt:
    log("\n🛑 Arrêt manuel par l'utilisateur.")
    sys.exit()
