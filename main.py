import requests

url = "https://api.aistudy.uz/api/StudyAILms/Account/Login"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://omp.aistudy.uz/",
    "Content-Type": "application/json",
    "Origin": "https://omp.aistudy.uz"
}

# username:password
# logins = [ "zamzanqodir14m", "muhammadyunus14m", "mubinaxon1222", "asilaxon14m", "shuxratjonov Bexruz", "murod1415", "mohichehra14m", "muhammadziyo2v", "gulazim", "e'ldor14", "Kamronbek14maktab", "sabina14m", "ruxshona14m"]
# logins = ["MUHAMMADRASUL:12345678a","HUSNIDAXON:12345678a","MUHAMMADZIYO:12345678a","MOHIGUL:12345678a"]
# logins =[
#     "sherzodbek14m:12345678a",
#     "imron14m:12345678a",
#     "xurshidbek2017:12345678a",
#     "javohir14m:12345678a",
#     "dinuraxon14m:12345678a",
#     "ramzanqodir14m:12345678a",
#     "ShuhratjonovBexruz:12345678a",
#     "mohichehra14m:12345678a",
#     "Kamronbek14maktab:12345678a",
#     "ruxshona14m:12345678a",
#     "sabina14m:12345678a",
#     "e`ldor14:12345678a",
#     "maxsudjon2018:12345678a",
#     "samiya142018:12345678a",
#     "oyattilo.14m:12345678a",
#     "malika14mm:12345678a",
#     "dilnura.14m:12345678a",
#     "fotima.14m:12345678a",
#     "asadbek.14:12345678a",
#     "halimjonb.14:12345678a",
#     "mziyo.14:12345678a",
#     "bibisora.14mm:12345678a",
#     "durdon14m:12345678a",
#     "mzohid.14:12345678a"
# ]
# logins = [
#     'muhammadrasul20154a:12345678a',
#     'HUSNIDAXON201514:12345678a',
#     'MOHIGUL20154a:12345678a',
#     'MUBINAXON20154a:12345678a',
#     'MAHSUDAXON20154A:12345678a',
#     'sirojiddin20154a:12345678a',
#     'madinaxon_299:12345678a',
#     'nuriddin20154a:12345678a',
#     'gulzira20154a:12345678a',
#     'muhammadziyo20154a.:12345678a',
#     'oftobxon20154a:12345678a',
#     'layloxon20154a:12345678a',
#     'sarvinoz20154a:12345678a',
#     'aloxon20154a:12345678a',
#     'SodiqjonovSolijon:12345678a',
#     'MUHAMMADALI20154a:12345678a',
#     'HIDOYATXON20154a:12345678a',
#     'UMARALI20154a:12345678a',
#     'muhlisa14m:12345678a',
#     'FOZILJON20154a:12345678a'
# ]
# logins = [
#     'MOHIGUL20154a:123456a',
#     'MUBINAXON20154a:123456a',
#     'MAHSUDAXON20154A:123456a',
#     'madinaxon_299:123456a',
#     'SodiqjonovSolijon:123456a'
# ]
# logins = ['muhammadali201514m:12345678a',"isnonjon14m:12345678a","nuriddin20154a:12345678a","robiyaxon20154a:12345678a","muhammadrasul20154a:12345678a"]
logins = [
    'PoziljonovMuhammadziyo:123456b',
    'SotinboyevMuhammadsodiq:123456b',
    'AbduqodirovAbduvohid:123456b',
    'O’ktamjonovMuhammadbobur:123456b',
    'ZokirjonovBekzodbek:123456b',
    'MahammadjonovaSevinch:123456b',
    'OdinayevaMehriniso:123456b',
    'Mo’ydinjonovShoxjaxon:123456b',
    'MamatovaMubina:123456b',
    'ShaxzodMamatisaqov:123456b',
    'KomilovOyatillo:123456b',
    'HaydaraliyevDilshodbek:123456b',
    'HabibullayevMuhammadyoqub:123456b',
    'AlijonovMansurbek:123456b',
    'AbdurasulovaMarjona:123456b'
]


j = "0cAFcWeA6w1P_cmNgUqyL-0i0WPigftKiAReWROxCoreyu6nz_YTznLLdfKKvyOXTAOg8KVdQ5dKgXtq3PSKgPkz2cDABqjgVZO34Q5GNJJYqsZ-84Ty43u062zlhlv6JBtA2smg7EnwNDZHbUyNT2JTpE07hcwfiZIN90dhYWpZR7eH22m8oRs_TLnrxmFWbEtF2QwHuPP3Eju1LZlFllMDz1-AEDmFEK-EZmCGpqN8nP2zL8bvL9uvqICfryTnNLnhwex06G9duZloGNtfECraHwlv9_TMtgxmnUzKu8VV7Q8NOHMgFTlVIystfLX4Zo-AyhD6CiyxOaZELqP5W3tm2y9pvq94kqGaKuMt63HxdjMolxJWwwp9P4TsA5G5x65Cl6GCk2Yqa6otvdMEeAl4BKtHNALWWOn7jikNiORVEWsDr-9unRsi_yL54FXA78EoL--24b2lT8hpjBUZKZ5mLmdsCCIqOawtQ7iDHc9HXrU93IlfcBe_83sJxiYnx46n2Z8ojDAHPKwLBRT0MBeLghFOF6sxm3rpOW_Uo-twfrqkWcjKcxiRfChcIvj5xVCOOOTvp-gtO8jC6Wfcd3ju8YAPn2NrWqDJsVI5pOCG4NQNDMQ3c9T_Hp-hJreslj1atlrmyO5y3AOcZFr1g_sUU6w65vMcTje6CcRtWPhAtOby9mEMvVbvB3wYtgYHpY13VHK6eW5v60WPwRRJROAfo1IFfsMY75W5Nti4A13Gi6X-Sx1TM2jOfByO_b7ylFhWdAlSNXwoLmCi5s0K6yfVbAWnDuAGdv-CnI5AXOBuBXxQEie__-HJC4oTC2VIhVEcwa_3gLZGi7n4TLpia4wV6zp0H6r3uhPXWssFk0VCyQjzCp9deQNsrVSIunPIYYkPGrZNUir1bRPU3e0T-N-NK_628F-e_o5_mAWns10sTOi6BujcadOHi4XhT4rPxOD4c7Yg4eV0kWIk9d4EmbszAc8gRQHpb88MaOMvlqDVuYo2zEjv9zep8i_uD0veHAyyvhJqn64aCr1WagkWmcbtpQNKu414o6OeoLYTT0SDsK1nlkaJMqn0PTikQXTm53vgMIWDKh6jIZpALRn-pmSxwKaENo31x8wjsLORc1RP3I3W7xvOtY9XcP7aapeF1XzCDImDZ3Zj3S2XlEzuJNPxU-jFUmLdeaez3i56Bnds2MBfwii-fq2ZFh6-SV5Ls2C8va-mjbtDr78Uf0BD7mWF7_DkA000oMrbSKqdzp1RrRc-Zj68-qEY_ajP7zkI0w-uRH_LLilERonSXkISsNREWXx2MHPXFtkuw8UkBxLrgE8pcHlwm0a77jfyedJNwfp6FPpYFBUCF1DeC-jff5hZJSIIMHVylNxb9qPM7QJhdqbh-L92smM1SFy3h93oEaP9hvlZWRAHL2Zrc7pCWyE4z6-LFE8lWmDEfxluObaCkpul8S9ftwgn_quuP46K564TfpFOVEf6ACl2y1kX0Cfbyx8SkIBHP7_7NuXa86mPp3kMmsm8wH8sB5nh931PpLNKn8vjD1MsWnuvt8X4Upl9aESqAaLjDs_8pBeW1_ajxC7ehkyQmi167aEOAT6iZeRoRSXwsrXR1bFDytBV8JrjqE0OggeAdJ-N7oVvow0kcMa8b-A35V4TpsvMoorCOZoHH6EVGUAHQqZ05yGkJstIXOiPZu0lq3RH3cXgRaKlgZ7TMQ8Ua2i9EFfmRaloTFyQQf7fcUFOylh4pktne1ouEwmznkEs88Lya3Z3JtxnDlFRNDrHMdbsl8KoqxRwnQUOj3ARDMIzb9Oz6Z-NwljpKRIw86Nq0pfdASeHs9OIv465U2OMQjM50LaReKklmq2YUrq7C0vDXIGFMlQld-PVQNaqzkLIPNKS0AqLb2nUHv_86tBIf53-lTlTdWVw62ZB5Lfiw0OaO5ObGoAaWhn5W1zRqTLhHiEf6AWhcxmqSOSDufQmqLvGw0tHf5KLUEtziDri85iI_d7lEZOWAyN_5ZiYjqDsMsMWMc9oCP7j91qAod9m1tJytziAP1ISl65NgLuHDMyTM_fcerPzZBqREu54sGTtUJCFA738R2SVRd-aLLutQRoKK1iI802c2Rkmd7x0oIjrxhRz8-a-a2x_Qd9mgIhYW3OYBE8_bLg-5yXlbVMkQlbz8pTK1SOiKzsI558BDMJQbApwiu1ezyl4f3DLbLiiMaE9SaR__VYwP5bxGOCMKjSdXMQIOJQvELS1BhK7Psi2GHQjWeMLoh9nlkKZDWev1C0Dwh4o3JjzUEymWy6slY_lUn-j7SdlrX5uNJyVdiwchDhLjAVt-Zk_INXrxj1mG8OtCdPI1HYTxthl3Ggn9V2KEtzhT8dasn0Kpq2XoUbvfA"

tokens = []

def func(login, password):
    payload = {
        "username": login,
        "password": f"{password}",
        "recaptchaToken": j
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)

        print(f"[{response.status_code}] {login}")

        data = response.json()
        print(data)
        # tokenni olish
        token = (
            data.get("result", {}).get("token")
            or data.get("token")
        )

        if token:
            bearer = f"Bearer {token}"

            # terminalga chiqaradi
            print(bearer)

            # listga saqlaydi
            tokens.append(bearer)

    except Exception as e:
        print(f"ERROR {login}: {e}")


if __name__ == "__main__":

    for item in logins:
        login, password = item.split(":")
        func(login, password)

    # faylga yozish
    with open("tokens.txt", "w") as f:
        for token in tokens:
            f.write(token + "\n")

    print(f"\nSaved {len(tokens)} tokens to tokens.txt")