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

document.addEventListener("DOMContentLoaded", function () {
  var paystackPublicKey = PAYSTACK_PUBLIC_KEY; // Set in template
  var userEmail = USER_EMAIL; // Set in template
  var accessKeyPrice = ACCESS_KEY_PRICE; // Set in template
  var callbackUrl = CALLBACK_URL; // Set in template
  var userID = USER_ID; // Set in template

  console.log("Paystack Public Key:", paystackPublicKey); // Debugging statement
  console.log("User Email:", userEmail); // Debugging statement
  console.log("Access Key Price:", accessKeyPrice); // Debugging statement
  console.log("Callback URL:", callbackUrl); // Debugging statement
  console.log("User ID:", userID); // Debugging statement

  const paymentMethodField = document.querySelector(
    'select[name="payment_method"]'
  );
  const cardFields = document.getElementById("card-fields");
  const momoFields = document.getElementById("momo-fields");
  const paystackBtn = document.getElementById("paystack-button");

  function clearFields(fields) {
    fields.querySelectorAll("input").forEach(function (input) {
      input.value = "";
    });
  }

  function toggleFields() {
    if (paymentMethodField.value === "card") {
      cardFields.style.display = "";
      momoFields.style.display = "none";
      clearFields(momoFields); // Clear mobile money fields
    } else if (paymentMethodField.value === "mtn_momo") {
      cardFields.style.display = "none";
      momoFields.style.display = "";
      clearFields(cardFields); // Clear card fields
    } else {
      cardFields.style.display = "none";
      momoFields.style.display = "none";
    }
  }

  paymentMethodField.addEventListener("change", toggleFields);
  toggleFields();

  if (paystackBtn) {
    paystackBtn.addEventListener("click", function (e) {
      e.preventDefault();

      // Initialize payment using Paystack Inline
      var handler = PaystackPop.setup({
        key: paystackPublicKey, // Set in template
        email: userEmail, // Set in template
        amount: accessKeyPrice * 100, // Convert to Pesewas
        currency: "GHS",
        metadata: {
          custom_fields: [
            {
              display_name: "User ID",
              variable_name: "user_id",
              value: userID,
            },
          ],
        },

        callback: function (response) {
          // Log the reference for debugging
          console.log("Payment reference:", response.reference);

          // Redirect to callback URL with reference
          window.location.href =
            callbackUrl + "?reference=" + response.reference;
        },
        onClose: function () {
          alert("Payment window closed.");
        },
      });

      handler.openIframe();
    });
  } else {
    console.error("Paystack button not found");
  }
});
