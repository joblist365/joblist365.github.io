// ===============================
// DATA: companies grouped by state arrays
// Keep structure and variable names (window.*Companies)
// Add `sector` field to enable sector filtering
// ===============================

// ANDHRA PRADESH COMPANIES
const andhraPradeshCompanies = [
  {
    company: "Wipro",
    state: "Andhra Pradesh",
    city: "Visakhapatnam",
    roles: ["Software Engineer", "Support Engineer", "QA Analyst"],
    linkedin: "https://www.linkedin.com/company/wipro",
    career: "https://careers.wipro.com",
    sector: "Information Technology"
  },
  {
    company: "Tech Mahindra",
    state: "Andhra Pradesh",
    city: "Vijayawada",
    roles: ["Developer", "UI Designer", "Tester"],
    linkedin: "https://www.linkedin.com/company/techmahindra",
    career: "https://careers.techmahindra.com",
    sector: "Information Technology"
  },
  {
    company: "Dr. Reddy’s Laboratories",
    state: "Andhra Pradesh",
    city: "Hyderabad",
    roles: ["Research Associate", "Quality Control", "Chemist"],
    linkedin: "https://www.linkedin.com/company/dr-reddy's-laboratories",
    career: "https://careers.drreddys.com",
    sector: "Pharmaceuticals"
  },
  {
    company: "Granules India",
    state: "Andhra Pradesh",
    city: "Hyderabad",
    roles: ["QC Analyst", "Production Chemist", "Lab Technician"],
    linkedin: "https://www.linkedin.com/company/granulesindia",
    career: "https://www.granulesindia.com/careers",
    sector: "Pharmaceuticals"
  },
  {
    company: "Amara Raja Batteries",
    state: "Andhra Pradesh",
    city: "Tirupati",
    roles: ["Production Engineer", "Maintenance Supervisor", "QA Inspector"],
    linkedin: "https://www.linkedin.com/company/amararaja",
    career: "https://www.amararaja.com/careers",
    sector: "Manufacturing"
  },
  {
    company: "Reliance Jio",
    state: "Andhra Pradesh",
    city: "Vijayawada",
    roles: ["Network Engineer", "Sales Executive", "Customer Support"],
    linkedin: "https://www.linkedin.com/company/reliance-jio",
    career: "https://careers.jio.com",
    sector: "Telecom"
  }
];

// KARNATAKA COMPANIES
const karnatakaCompanies = [
  {
    company: "Infosys",
    state: "Karnataka",
    city: "Bangalore",
    roles: ["Software Engineer", "Data Scientist"],
    linkedin: "https://www.linkedin.com/company/infosys",
    career: "https://www.infosys.com/careers",
    sector: "Information Technology"
  },
  {
    company: "Flipkart",
    state: "Karnataka",
    city: "Bangalore",
    roles: ["Product Manager", "SDE", "Data Analyst"],
    linkedin: "https://www.linkedin.com/company/flipkart",
    career: "https://www.flipkartcareers.com",
    sector: "Ecommerce"
  }
];

// MAHARASHTRA COMPANIES
const maharashtraCompanies = [
  {
    company: "Tata Motors",
    state: "Maharashtra",
    city: "Pune",
    roles: ["Mechanical Engineer", "Production Supervisor"],
    linkedin: "https://www.linkedin.com/company/tata-motors",
    career: "https://careers.tatamotors.com",
    sector: "Automotive"
  },
  {
    company: "Reliance Industries",
    state: "Maharashtra",
    city: "Mumbai",
    roles: ["Chemical Engineer", "Business Analyst"],
    linkedin: "https://www.linkedin.com/company/reliance-industries-limited",
    career: "https://www.ril.com/Careers",
    sector: "Energy"
  }
];

// TAMIL NADU COMPANIES
const tamilNaduCompanies = [
  {
    company: "TVS Motor",
    state: "Tamil Nadu",
    city: "Chennai",
    roles: ["Assembly Technician", "Design Engineer"],
    linkedin: "https://www.linkedin.com/company/tvs-motor",
    career: "https://www.tvsmotor.com/careers",
    sector: "Automotive"
  },
  {
    company: "Apollo Hospitals",
    state: "Tamil Nadu",
    city: "Chennai",
    roles: ["Doctor", "Nurse", "Lab Technician"],
    linkedin: "https://www.linkedin.com/company/apollo-hospitals",
    career: "https://www.apollohospitals.com/careers",
    sector: "Healthcare"
  }
];

// DELHI COMPANIES
const delhiCompanies = [
  {
    company: "HCLTech",
    state: "Delhi",
    city: "New Delhi",
    roles: ["Software Engineer", "Cloud Engineer"],
    linkedin: "https://www.linkedin.com/company/hcltech",
    career: "https://www.hcltech.com/careers",
    sector: "Information Technology"
  },
  {
    company: "OYO",
    state: "Delhi",
    city: "New Delhi",
    roles: ["Operations Manager", "Sales Executive"],
    linkedin: "https://www.linkedin.com/company/oyorooms",
    career: "https://careers.oyorooms.com",
    sector: "Hospitality"
  }
];

// Expose arrays to window for results page consumption (structure preserved)
window.andhraPradeshCompanies = andhraPradeshCompanies;
window.karnatakaCompanies = karnatakaCompanies;
window.maharashtraCompanies = maharashtraCompanies;
window.tamilNaduCompanies = tamilNaduCompanies;
window.delhiCompanies = delhiCompanies;
