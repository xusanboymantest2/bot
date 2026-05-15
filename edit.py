import requests
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Passport data from your list
passports = [
    ("01.05.2015", "I-AN", "0784014"),
    ("28.11.2015", "I-AN", "0830858"),
    ("15.09.2015", "I-AN", "0795676"),
    ("11.09.2015", "I-AN", "0812391"),
    ("04.07.2015", "I-AN", "0784108"),
    ("04.12.2015", "I-AN", "0830920"),
    ("26.03.2015", "I-AN", "0765233"),
    ("14.05.2015", "I-AN", "0783536"),
    ("25.03.2015", "I-AN", "0765225"),
    ("19.08.2015", "I-AN", "0783343"),
    ("01.05.2015", "I-AN", "0783341"),
    ("14.09.2015", "I-AN", "0812542"),
    ("11.04.2015", "III-AN", "0112281"),
    ("16.04.2015", "I-AN", "0765402"),
    ("02.02.2015", "I-AN", "0759486"),
    ("04.11.2015", "I-AN", "0830568"),
    ("19.08.2015", "I-AN", "0830593"),
    ("14.09.2015", "I-AN", "0812732"),
    ("25.05.2015", "I-AN", "0783630"),
    ("28.08.2015", "I-AN", "0812155"),
    ("05.10.2015", "I-AN", "0812853"),
    ("12.12.2015", "I-AN", "0830980"),
    ("31.08.2015", "I-AN", "0812208"),
    ("06.05.2015", "I-AN", "0783366"),
    ("15.09.2015", "I-AN", "0812538"),
    ("27.10.2015", "I-AN", "0830384"),
    ("08.10.2015", "I-AN", "0812881"),
    ("28.09.2015", "I-AN", "0812787"),
    ("12.06.2015", "I-SU", "0642942"),
]

URL = "https://api.aistudy.uz/api/StudyAILms/Account/GetPersonDataFromGcp"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:150.0) Gecko/20100101 Firefox/150.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://omp.aistudy.uz/',
    'Content-Type': 'application/json',
    'Origin': 'https://omp.aistudy.uz',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Priority': 'u=0'
}

RECAPTCHA_TOKEN = "0cAFcWeA5dxMgoWGykxQtEEONBR-FJKImhQuUM3W5noEPYPJVrefAF-ztJfE1Z2PjBrQOsc_NWD8k3ayx7gRQax7Crlp_jAFj9J19FFRn4BaF23m9OuXkoJR0we4AOhwaHPGiobCJtmoYqSZ45vxLnwRlCJwbUnK_c-5H8cF1i2dGd3wQlgWJZIxo2f3ypEyEsAiZrnUvZuLkcPU6KtQ-9R2_T8yEYzlDV1dA--zRftqkaLWhpASOwHN32fShEG_le84h6psmGn2U_Q_mpfwBJDDUAn58JGAOMW2vLFmyGTGAbQvqBM-pQYO72lnNRce0zDFpRaKlMUFl15ZG3JT-DN0sLHWHL_h7hQ3en0vomQqyXti5LfAeGAGtI17GdkKVExLzada9L2m4rA0xsfkzCRqDBnlbfBJsQdqaOuQlNeZSRDV3QLzZNF0R7gT0BfdYYWjCnANCT4xVK1TeHwF5-HL7ZHFI6LWDHkskO5AL7neB3hiu-4j5uXoLkJ3F6JLLVydv-6MFZ_n7QNAoyCzM-lR2CAV43rEtroFSmFeFI_4DYRdyMZOocKMo1MICvJ26eHyo0HbX6076cOJyBO0GMK2E3I4oY23q-LazmY5YcroxYXQYLltF4DXeCiDtpUxkrKbZ8HLyddEp1u82ZFWn1xrKGLkFOFNyVKpXSK8S1i_iHckLWiSseZtyCajbVBobF7Ym4oofKf7lsF3zvSEDCG1TjC8s_u1G5C4PmgLkgf_aKEkOoiopuntrLN0MLvsaKrMXpE4DwxXHliMunxDrupXxDGMQuFHX7hSrfPBhn9RjjFdyFOxdPE0Gbbci9gZbCxEFxshfE3hJiWbRD-aytn8vJu3f32rbWACGj6Jthsl1A6IKaO4MplD3CUOgMws5bPNCDFPoz_JzcT1Q--TcYI_Btf89TTtwnN_fg1NlfJUVu_zifurMiQkmjzplXYQaS_kiNJIuCwsn-2AulI_DkuD29tZL3zVdn4FwWnr16PahHNFN75Kr_WpJyfZC59ofAs_eAiCLkBsgAEbBmqUVs9Ez62GXflCCtwWA4ydhgugFG1AliTBi5rlveVulO5PSkswU4Y4eOIfMSoCELUP_B9y7898qVhnpQYZLGw4KnZ4VWNkd_1s-D1p5oon2IvnzLxjpJqUYoUa5dhggwUKZs3KsJuFSot043HoodFnOWEYgP288jVSuKexhMShGDxvUhfJk5He_8B2aYkQHBRN1Kjezm7x1oQ1p6VpfjjQsIZcWT_OAhf39dCcLnbEihs4vd5YQ1BUDWwgQMdDH2KEeYeT4vnLysgcB_UQOiq1EQ-gY9o1A5CFuqNAvnrhSxUAZ710lEZGloK-UvLn62DyB9mWZMKdw4dYJwWbKTYG_nWVZb4H4_zrHSFxcOWVMJD8AXlBSb62ygYSk34tBZM98NIRrpXe70sPLIvfA6F4PsATGwl_lBw5nymE71Yl9Aod3bVJXzjMQ8XHT7hRwmocPiPTxQmCbRxPK2EIItliy75q7D0eKhwcfk1orHtcD79m8pZZCLRgC7VK4pGWP_moWw5saiPtTudbdrcLMGaaEtA0ooKIc0Tkhu-iQyXIKCIx64paF7zFGcGV2z8NiZWNMVOssMc3gD8KXPrQ2N-_Om7sFmnUrv_Pem4dIwzlY6yUU8yJamOcFPK--91jxOmYxQ9B-8MAMKWMnqMRBsE2jhEW47U6scZX1lYOkpvDKNWMLsDY-5yYBBwS1WHh3rV35SEkcNVZ08rT9JJKS3QzXe_di9uoWsLe85G8stjc1U23hOk-iSMtJsxHK5NNRYEjwadyEewObdx8CG0WuGnV0z043f-BuvIUptavgeMZZuiZXCxNFDzY7Jd9W55CZSj3_gU-CGWA9_i54OBgNRLXg9YNmFQctOq_XaIi1vH4aV8vLT6WadkeMH9An_73OvzWZN_LUt-X5h71uFJYmuzlBal16VTmEWPIULbTk3by-oW4CyXOv6oPVAXCkZVPyLiRYosxcJLmSlSPpzK2Qy7KHSuRu18Wn8u2Ovkro3ETn03hEB7klwzJUST_UfkBSQZuDEPlNxaHS4j-xl2_Jxe8rzottcyeHCilWW75yYa5T0kZ1kw332mcdvcSvoblmYxErhkAm0aaUxP_1u-Q"  # Empty as you specified

def convert_date(date_str):
    """Convert DD.MM.YYYY to YYYY-MM-DD"""
    d, m, y = date_str.split('.')
    return f"{y}-{m}-{d}"

def send_request(birthdate, seria, number):
    """Send single request and return response"""
    payload = {
        "documentType": 2,
        "seria": seria,
        "number": number,
        "birthdate": convert_date(birthdate),
        "recaptchaToken": RECAPTCHA_TOKEN
    }
    
    try:
        response = requests.post(URL, headers=HEADERS, json=payload, timeout=10)
        return {
            'passport': f"{seria}{number}",
            'birthdate': birthdate,
            'status': response.status_code,
            'response': response.text,
            'success': response.status_code == 200
        }
    except Exception as e:
        return {
            'passport': f"{seria}{number}",
            'birthdate': birthdate,
            'status': 'ERROR',
            'response': str(e),
            'success': False
        }

def main():
    print(f"Starting requests for {len(passports)} passports...\n")
    
    results = []
    success_count = 0
    
    # Sequential execution (switch to ThreadPoolExecutor for parallel)
    for birthdate, seria, number in passports:
        result = send_request(birthdate, seria, number)
        results.append(result)
        
        status_icon = "✓" if result['success'] else "✗"
        print(f"{status_icon} {seria}{number} ({birthdate}) - {result['status']}")
        
        if result['success']:
            success_count += 1
            print(f"   Response: {result['response'][:200]}")  # First 200 chars
        
        print()
    
    # Summary
    print("\n" + "="*60)
    print(f"SUMMARY: {success_count}/{len(passports)} successful")
    print("="*60)
    
    # Save results to JSON
    with open('a.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\nFull results saved to results.json")

if __name__ == "__main__":
    main()