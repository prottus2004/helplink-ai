export const languageMap = {
  "Hindi": { name: "Hindi", native: "हिन्दी", flag: "🇮🇳", code: "HI" },
  "Malayalam": { name: "Malayalam", native: "മലയാളം", flag: "🌴", code: "ML" },
  "Tamil": { name: "Tamil", native: "தமிழ்", flag: "🛕", code: "TA" },
  "Bengali": { name: "Bengali", native: "বাংলা", flag: "🌾", code: "BN" },
  "Odia": { name: "Odia", native: "ଓଡ଼ିଆ", flag: "🌊", code: "OR" },
  "Telugu": { name: "Telugu", native: "తెలుగు", flag: "🎻", code: "TE" },
  "Marathi": { name: "Marathi", native: "मराठी", flag: "🏰", code: "MR" },
  "Kannada": { name: "Kannada", native: "ಕನ್ನಡ", flag: "🏵️", code: "KN" },
  "Gujarati": { name: "Gujarati", native: "ગુજરાતી", flag: "🏺", code: "GU" },
  "Punjabi": { name: "Punjabi", native: "ਪੰਜਾਬੀ", flag: "🌾", code: "PJ" },
  "English": { name: "English", native: "English", flag: "🇬🇧", code: "EN" }
};

export const getLanguageLabel = (lang) => {
  const normalized = lang ? lang.trim() : "English";
  const match = languageMap[normalized] || languageMap["English"];
  return `${match.flag} ${match.name} (${match.native})`;
};

export const getLanguageFlag = (lang) => {
  const normalized = lang ? lang.trim() : "English";
  const match = languageMap[normalized] || languageMap["English"];
  return match.flag;
};
