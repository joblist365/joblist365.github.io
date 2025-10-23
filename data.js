// ===============================
// ANDHRA PRADESH COMPANIES
// ===============================
const andhraPradeshCompanies = [
  {
    company: "Wipro",
    state: "Andhra Pradesh",
    city: "Visakhapatnam",
    roles: ["Software Engineer", "Support Engineer", "QA Analyst"],
    linkedin: "https://www.linkedin.com/company/wipro",
    career: "https://careers.wipro.com"
  },
  {
    company: "Tech Mahindra",
    state: "Andhra Pradesh",
    city: "Vijayawada",
    roles: ["Developer", "UI Designer", "Tester"],
    linkedin: "https://www.linkedin.com/company/techmahindra",
    career: "https://careers.techmahindra.com"
  },
  {
    company: "Dr. Reddy’s Laboratories",
    state: "Andhra Pradesh",
    city: "Hyderabad",
    roles: ["Research Associate", "Quality Control", "Chemist"],
    linkedin: "https://www.linkedin.com/company/dr-reddy's-laboratories",
    career: "https://careers.drreddys.com"
  },
  {
    company: "Granules India",
    state: "Andhra Pradesh",
    city: "Hyderabad",
    roles: ["QC Analyst", "Production Chemist", "Lab Technician"],
    linkedin: "https://www.linkedin.com/company/granulesindia",
    career: "https://www.granulesindia.com/careers"
  }
  // add remaining companies here as before...
];

// ✅ Safe global exports (no data loss)
window.andhraPradeshCompanies = window.andhraPradeshCompanies || (typeof andhraPradeshCompanies !== 'undefined' ? andhraPradeshCompanies : []);
window.karnatakaCompanies   = window.karnatakaCompanies   || [];
window.maharashtraCompanies = window.maharashtraCompanies || [];
window.tamilNaduCompanies   = window.tamilNaduCompanies   || [];
window.delhiCompanies       = window.delhiCompanies       || [];
