document.addEventListener("DOMContentLoaded", function() {
  const inputs = document.querySelectorAll("input[list]");

  inputs.forEach(input => {
    const datalist = document.getElementById(input.getAttribute("list"));
    const options = Array.from(datalist.options).map(opt => opt.value);

    input.addEventListener("input", function() {
      const val = this.value.toLowerCase();
      datalist.innerHTML = "";

      options
        .filter(opt => opt.toLowerCase().includes(val))
        .forEach(opt => {
          const optionElement = document.createElement("option");
          optionElement.value = opt;
          datalist.appendChild(optionElement);
        });
    });
  });
});
