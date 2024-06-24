document.addEventListener("DOMContentLoaded", function () {
  // Toggle log visibility functionality
  var toggleLogButton = document.getElementById("toggle-log");
  var keyLog = document.getElementById("key-log");

  // Check if elements exist before adding event listeners
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
  // Paystack integration
  var paystackPublicKey = PAYSTACK_PUBLIC_KEY; // Set in template
  var userEmail = USER_EMAIL; // Set in template
  var accessKeyPrice = ACCESS_KEY_PRICE; // Set in template
  var callbackUrl = CALLBACK_URL; // Set in template
  var userID = USER_ID; // Set in template

  // Debugging statements
  console.log("Paystack Public Key:", paystackPublicKey);
  console.log("User Email:", userEmail);
  console.log("Access Key Price:", accessKeyPrice);
  console.log("Callback URL:", callbackUrl);
  console.log("User ID:", userID);

  // Get payment method dropdown and fields
  const paymentMethodField = document.querySelector(
    'select[name="payment_method"]'
  );
  const cardFields = document.getElementById("card-fields");
  const momoFields = document.getElementById("momo-fields");
  const paystackBtn = document.getElementById("paystack-button");

  // Function to clear input fields
  function clearFields(fields) {
    fields.querySelectorAll("input").forEach(function (input) {
      input.value = "";
    });
  }

  // Function to toggle payment method fields
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

  // Add event listener for payment method change
  if (paymentMethodField) {
    paymentMethodField.addEventListener("change", toggleFields);
    toggleFields();
  }

  // Add event listener for Paystack button
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

        // Callback function for successful payment
        callback: function (response) {
          // Log the reference for debugging
          console.log("Payment reference:", response.reference);

          // Redirect to callback URL with reference
          window.location.href =
            callbackUrl + "?reference=" + response.reference;
        },
        // Function for handling closed payment window
        onClose: function () {
          alert("Payment window closed.");
        },
      });

      // Open Paystack payment window
      handler.openIframe();
    });
  } else {
    console.error("Paystack button not found");
  }
});
