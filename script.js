<script>
  // Data
  const cityOptions = {
    "Andhra Pradesh": ["Hyderabad", "Vijayawada", "Visakhapatnam", "Guntur"],
    "Karnataka": ["Bangalore", "Mysore", "Mangalore"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
    "Delhi": ["New Delhi", "Dwarka", "Saket"]
  };

  function updateCities() {
    const state = document.getElementById('state').value;
    const citySelect = document.getElementById('city');
    citySelect.innerHTML = '<option value="">Select City</option>';
    if (state && cityOptions[state]) {
      cityOptions[state].forEach(city => {
        const option = document.createElement('option');
        option.value = city;
        option.textContent = city;
        citySelect.appendChild(option);
      });
    }
  }

  // Make dropdowns typeable
  function makeTypeable(selectId) {
    const select = document.getElementById(selectId);
    const input = document.createElement("input");
    input.setAttribute("placeholder", select.options[0].text);
    input.style.width = "100%";
    input.style.padding = "10px";
    input.style.border = "1px solid #ccc";
    input.style.borderRadius = "8px";
    input.style.marginBottom = "12px";
    input.style.fontSize = "1rem";

    select.style.display = "none";
    select.parentNode.insertBefore(input, select);

    input.addEventListener("input", () => {
      const filter = input.value.toLowerCase();
      const match = Array.from(select.options).find(opt =>
        opt.text.toLowerCase().startsWith(filter)
      );
      if (match) {
        select.value = match.value;
      }
    });

    input.addEventListener("blur", () => {
      input.value = select.value;
    });
  }

  ["sector", "state", "city", "role"].forEach(makeTypeable);

  function searchJobs() {
    const sector = document.getElementById('sector').value;
    const state = document.getElementById('state').value;
    const city = document.getElementById('city').value;
    const role = document.getElementById('role').value;

    if (!sector) {
      alert("Please select a sector first.");
      return;
    }

    alert(`Searching ${sector} jobs${state ? ' in ' + state : ''}${city ? ', ' + city : ''}${role ? ' for ' + role : ''}.`);
  }
</script>
