document.addEventListener("DOMContentLoaded", function () {
  const paymentMethodField = document.querySelector(
    'select[name="payment_method"]'
  );
  const cardFields = document.getElementById("card-fields");
  const momoFields = document.getElementById("momo-fields");

  function clearFields(fields) {
    if (fields) {
      fields.querySelectorAll("input").forEach(function (input) {
        input.value = "";
      });
    }
  }

  function toggleFields() {
    if (paymentMethodField.value === "card") {
      cardFields.style.display = "block";
      momoFields.style.display = "none";
      clearFields(momoFields);
    } else if (paymentMethodField.value === "mtn_momo") {
      cardFields.style.display = "none";
      momoFields.style.display = "block";
      clearFields(cardFields);
    } else {
      cardFields.style.display = "none";
      momoFields.style.display = "none";
    }
  }

  if (paymentMethodField) {
    paymentMethodField.addEventListener("change", toggleFields);
    toggleFields(); // Call once to set initial state
  }
});
