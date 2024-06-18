document.addEventListener("DOMContentLoaded", function () {
  var toggleLogButton = document.getElementById("toggle-log");
  var keyLog = document.getElementById("key-log");

  toggleLogButton.addEventListener("click", function () {
    if (keyLog.style.maxHeight) {
      keyLog.style.maxHeight = null;
      toggleLogButton.textContent = "View Logs";
    } else {
      keyLog.style.maxHeight = keyLog.scrollHeight + "px";
      toggleLogButton.textContent = "Hide Logs";
    }
  });
});

// document.addEventListener("DOMContentLoaded", function () {
//   const paymentMethodField = document.querySelector(
//     'select[name="payment_method"]'
//   );
//   const cardFields = document.getElementById("card-fields");
//   const momoFields = document.getElementById("momo-fields");
//   const cardErrorMessages = document.getElementById("card-error-messages");
//   const momoErrorMessages = document.getElementById("momo-error-messages");

//   function toggleFields() {
//     if (paymentMethodField.value === "Card") {
//       cardFields.style.display = "";
//       momoFields.style.display = "none";
//     } else if (paymentMethodField.value === "MTN") {
//       cardFields.style.display = "none";
//       momoFields.style.display = "";
//     } else {
//       cardFields.style.display = "none";
//       momoFields.style.display = "none";
//     }
//   }

//   function displayErrors() {
//     const errorElements = document.querySelectorAll(".errorlist");
//     errorElements.forEach(function (errorElement) {
//       const fieldName =
//         errorElement.previousElementSibling.getAttribute("name");
//       if (["card_number", "card_expiry", "card_cvv"].includes(fieldName)) {
//         cardFields.style.display = "";
//         cardErrorMessages.appendChild(errorElement);
//       }
//       if (fieldName === "mobile_money_number") {
//         momoFields.style.display = "";
//         momoErrorMessages.appendChild(errorElement);
//       }
//     });
//   }

//   paymentMethodField.addEventListener("change", toggleFields);
//   toggleFields(); // Initialize the display based on the current value
//   displayErrors(); // Display errors if any
// });

document.addEventListener("DOMContentLoaded", function () {
  const paymentMethodField = document.querySelector(
    'select[name="payment_method"]'
  );
  const cardFields = document.getElementById("card-fields");
  const momoFields = document.getElementById("momo-fields");
  const cardErrorMessages = document.getElementById("card-error-messages");
  const momoErrorMessages = document.getElementById("momo-error-messages");

  function clearFields(fields) {
    fields.querySelectorAll("input").forEach(function (input) {
      input.value = "";
    });
  }

  function toggleFields() {
    if (paymentMethodField.value === "Card") {
      cardFields.style.display = "";
      momoFields.style.display = "none";
      clearFields(momoFields); // Clear mobile money fields
    } else if (paymentMethodField.value === "MTN") {
      cardFields.style.display = "none";
      momoFields.style.display = "";
      clearFields(cardFields); // Clear card fields
    } else {
      cardFields.style.display = "none";
      momoFields.style.display = "none";
    }
  }

  function displayErrors() {
    const errorElements = document.querySelectorAll(".errorlist");
    errorElements.forEach(function (errorElement) {
      const fieldName =
        errorElement.previousElementSibling.getAttribute("name");
      if (["card_number", "card_expiry", "card_cvv"].includes(fieldName)) {
        cardFields.style.display = "";
        cardErrorMessages.appendChild(errorElement);
      }
      if (fieldName === "mobile_money_number") {
        momoFields.style.display = "";
        momoErrorMessages.appendChild(errorElement);
      }
    });
  }

  paymentMethodField.addEventListener("change", toggleFields);
  toggleFields(); // Initialize the display based on the current value
  displayErrors(); // Display errors if any
});
