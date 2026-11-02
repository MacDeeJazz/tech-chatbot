import os
import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from django.conf import settings

nlp = spacy.load("en_core_web_sm")

INTERACTIVE_FLOWS = {
    "boot_failure_wizard": (
        "Ah, dealing with a machine that won't start can definitely be stressful! Let's take it one calm step at a time so we don't risk your files.\n\n"
        "To get us started on the right foot: **Is this a desktop or a laptop, and do you see any lights or hear any fans spin when you press the power button?**"
    ),
    "blue_screen_wizard": (
        "Ugh, a Blue Screen of Death is never fun to look at. Don't worry, we can track down what caused the crash.\n\n"
        "To start off light: **Do you remember what you were doing right before it crashed, or did it happen out of nowhere?**"
    ),
    "overheating_wizard": (
        "It sounds like your system is running way too hot! Let's get those temperatures under control before anything gets damaged.\n\n"
        "Quick first question: **Are the cooling fans making a loud screaming noise, or are they completely silent and dead?**"
    ),
    "network_wizard": (
        "Network dropouts can drive anyone crazy. Let's get your connection stable again.\n\n"
        "First things first: **Is this affecting just your computer, or are other devices in the house losing Wi-Fi too?**"
    )
}

# Comprehensive 4-Step Professional Technician Knowledge Base
KNOWLEDGE_BASE = {
    "blue_screen": {
        "solution": (
            "1. **Analyze Minidump:** Navigate to `C:\\Windows\\Minidump` and analyze `.dmp` files using BlueScreenView or WinDbg to find the faulting driver.\n"
            "2. **Repair System Files:** Run `DISM /Online /Cleanup-Image /RestoreHealth`, then `sfc /scannow` in Admin CMD.\n"
            "3. **Driver Rollback:** Boot into Safe Mode and roll back recent GPU or chipset updates via Device Manager.\n"
            "4. **Memory Diagnostic:** Run Windows Memory Diagnostic (`mdsched.exe`) to check for unstable memory modules."
        )
    },
    "no_wifi": {
        "solution": (
            "1. **Reset Network Stack:** Run `netsh winsock reset`, `netsh int ip reset`, and `ipconfig /flushdns` in admin CMD.\n"
            "2. **Power Management:** Uncheck 'Allow the computer to turn off this device to save power' in Device Manager properties.\n"
            "3. **Physical / BIOS Check:** Verify that the Wi-Fi card is enabled in BIOS/UEFI and physical switches.\n"
            "4. **IP Configuration:** Run `ipconfig /all` to verify your default gateway and DHCP lease."
        )
    },
    "overheating": {
        "solution": (
            "1. **Thermal Audit:** Use HWMonitor or Core Temp to audit idle vs load temperatures.\n"
            "2. **Physical Maintenance:** Clean dust mat accumulations from cooling fins and intake vents using compressed air.\n"
            "3. **Thermal Paste:** Remove the heatsink assembly, clean old paste with 99% isopropyl alcohol, and reapply fresh thermal paste.\n"
            "4. **Fan Tachometer Check:** Ensure CPU/GPU fans are spinning freely and reporting proper RPM."
        )
    },
    "no_power": {
        "solution": (
            "1. **Power Drain:** Unplug AC cord and battery, hold power button for 30–60 seconds to discharge residual capacitor energy.\n"
            "2. **PSU Paperclip Test:** Bridge the Green wire to any Black ground wire on the 24-pin ATX connector to test internal PSU fan startup.\n"
            "3. **Front Panel Audit:** Verify front panel header connections (`PWR_BTN`) or bridge pins with a screwdriver.\n"
            "4. **Bare-Minimum Bench Test:** Strip the system down to motherboard, CPU, cooler, and 1 stick of RAM outside the chassis."
        )
    },
    "ram_failure": {
        "solution": (
            "1. **Reseat Modules:** Clean gold contacts with a clean eraser or isopropyl alcohol and re-seat RAM firmly into slots.\n"
            "2. **Single-Stick Isolation:** Test individual RAM sticks one by one in primary slots to isolate a dead module.\n"
            "3. **CPU Mounting Pressure:** Check for over-tightened CPU coolers or bent socket pins affecting memory channels.\n"
            "4. **Extended MemTest86:** Boot a USB running MemTest86 to execute a multi-pass memory sweep."
        )
    },
    "hard_drive": {
        "solution": (
            "1. **BIOS / UEFI Detection:** Verify if UEFI/BIOS detects the SATA or NVMe physical drive presence.\n"
            "2. **S.M.A.R.T. Audit:** Use CrystalDiskInfo to inspect health attributes like reallocated sectors.\n"
            "3. **File Repair:** Run `chkdsk C: /f /r /x` from recovery command prompt to fix corrupt file indexes.\n"
            "4. **Cable Swap:** Replace damaged SATA data cables or reseat M.2 NVMe drives in alternate slots."
        )
    },
    "motherboard": {
        "solution": (
            "1. **Visual Component Inspection:** Inspect electrolytic capacitors for bulging tops or electrolyte leakage.\n"
            "2. **Clear CMOS:** Remove the CR2032 coin cell battery for 5 minutes or bridge jumper pins to reset NVRAM.\n"
            "3. **Standoff Audit:** Check for unneeded chassis standoffs causing electrical short-circuits on back traces.\n"
            "4. **BIOS Flash Recovery:** Utilize built-in motherboard USB flashback features if firmware is corrupted."
        )
    },
    "power_supply": {
        "solution": (
            "1. **Multimeter Rail Check:** Measure DC voltages on +12V rails under load (should read between 11.4V and 12.6V).\n"
            "2. **Sensory Inspection:** Check for burnt plastic odors, clicking relay switches, or failing fan bearings.\n"
            "3. **Over-Current Protection Test:** Disconnect high-draw peripherals to check for sudden shutdown triggers.\n"
            "4. **Load Substitution:** Swap in a known-working test bench power supply unit to confirm permanent failure."
        )
    }
}

# Load training data dynamically from CSV
csv_path = os.path.join(settings.BASE_DIR, 'chatbot_training_data.csv')
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    X = df['text']
    y = df['intent']
else:
    X = ["blue screen error", "wifi not working"]
    y = ["blue_screen", "no_wifi"]

ml_classifier = make_pipeline(TfidfVectorizer(), LogisticRegression())
ml_classifier.fit(X, y)

def get_troubleshooting_response(user_query, active_wizard=None):
    query_lower = user_query.lower()

    # 1. Flexible Multi-Turn Context Resolution
    if active_wizard == "network_wizard":
        return KNOWLEDGE_BASE["no_wifi"]["solution"], None
    
    if active_wizard == "boot_failure_wizard":
        if any(w in query_lower for w in ["no lights", "no fans", "nothing", "dead", "desktop", "laptop"]):
            return KNOWLEDGE_BASE["no_power"]["solution"], None
        elif any(w in query_lower for w in ["logo", "stuck", "frozen", "bootable", "os not found", "screen stays black"]):
            return KNOWLEDGE_BASE["hard_drive"]["solution"], None
        elif any(w in query_lower for w in ["beep", "beeping", "lights"]):
            return KNOWLEDGE_BASE["ram_failure"]["solution"], None
        return KNOWLEDGE_BASE["no_power"]["solution"], None

    if active_wizard == "blue_screen_wizard":
        return KNOWLEDGE_BASE["blue_screen"]["solution"], None

    if active_wizard == "overheating_wizard":
        return KNOWLEDGE_BASE["overheating"]["solution"], None

    # 2. Check for New Wizard Triggers (First Turn)
    startup_phrases = ["wont start", "won't start", "wont boot", "won't boot", "wont turn on", "won't turn on", "cant start", "cant boot"]
    if any(phrase in query_lower for phrase in startup_phrases) and len(query_lower.split()) < 6:
        return INTERACTIVE_FLOWS["boot_failure_wizard"], "boot_failure_wizard"

    bsod_phrases = ["blue screen", "bsod", "stop code", "critical process died"]
    if any(phrase in query_lower for phrase in bsod_phrases) and len(query_lower.split()) < 6:
        return INTERACTIVE_FLOWS["blue_screen_wizard"], "blue_screen_wizard"

    overheat_phrases = ["overheating", "overheat", "running hot", "laptop hot", "fans loud"]
    if any(phrase in query_lower for phrase in overheat_phrases) and len(query_lower.split()) < 6:
        return INTERACTIVE_FLOWS["overheating_wizard"], "overheating_wizard"

    wifi_phrases = ["wifi", "wireless", "no internet", "disconnecting", "network adapter"]
    if any(phrase in query_lower for phrase in wifi_phrases) and len(query_lower.split()) < 6:
        return INTERACTIVE_FLOWS["network_wizard"], "network_wizard"

    # 3. Standard Keyword Mapping for Direct Queries
    keyword_mapping = {
        "hard_drive": ["hard drive", "ssd", "disk", "clicking", "smart", "chkdsk", "bootable", "boot device", "os not found", "unbootable"],
        "motherboard": ["motherboard", "capacitor", "bios", "pcie", "standoff"],
        "power_supply": ["power supply", "psu", "rail", "voltage", "ticking", "burning", "24-pin"],
        "ram_failure": ["ram", "memory", "dimm", "beep", "slot"],
        "blue_screen": ["blue screen", "bsod", "stop code", "crash", "restart loop"],
        "no_wifi": ["wifi", "wireless", "internet", "adapter", "ipconfig"],
        "overheating": ["overheating", "hot", "fan", "thermal", "temperature"],
        "no_power": ["no power", "dead"]
    }

    for intent, keywords in keyword_mapping.items():
        for kw in keywords:
            if kw in query_lower:
                return KNOWLEDGE_BASE[intent]["solution"], None

    # 4. Machine Learning Fallback
    try:
        doc = nlp(query_lower)
        processed_query = " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])

        if len(processed_query.split()) >= 2:
            predicted_intent = ml_classifier.predict([processed_query])[0]
            probabilities = ml_classifier.predict_proba([processed_query])[0]
            max_prob = max(probabilities)

            if max_prob > 0.25 and predicted_intent in KNOWLEDGE_BASE:
                return KNOWLEDGE_BASE[predicted_intent]["solution"], None
    except Exception as e:
        print(f"ML Error: {e}")

    if active_wizard:
        return "Thanks for that detail! Based on what you've described, I recommend checking your power connections, resetting your system state, or testing your components individually.", None

    return "I am not confident I understand that technical issue. Try describing hardware symptoms like 'no lights or fans', 'stuck on logo', 'computer overheating', or 'blue screen'.", None