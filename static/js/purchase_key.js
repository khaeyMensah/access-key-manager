/**
 * Event listener for DOMContentLoaded to ensure the script runs after the DOM is fully loaded.
 */
document.addEventListener("DOMContentLoaded", function () {
  // Paystack integration
  let paystackPublicKey = PAYSTACK_PUBLIC_KEY; // Paystack public key from the template
  let userEmail = USER_EMAIL; // User email from the template
  let accessKeyPrice = ACCESS_KEY_PRICE; // Access key price from the template
  let callbackUrl = CALLBACK_URL; // Callback URL from the template

  // Get payment method dropdown and corresponding field sections
  const paymentMethodField = document.querySelector(
    'select[name="payment_method"]'
  );
  const cardFields = document.getElementById("card-fields");
  const momoFields = document.getElementById("momo-fields");
  const paystackBtn = document.getElementById("paystack-button");
  const paymentForm = document.getElementById("paymentForm");

  /**
   * Clear input fields within a specified fieldset.
   * @param {HTMLElement} fields - The fieldset containing input fields to be cleared.
   */
  function clearFields(fields) {
    fields.querySelectorAll("input").forEach(function (input) {
      input.value = "";
    });
  }

  /**
   * Toggle the visibility of payment method fields based on the selected payment method.
   */
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

  // Add event listener for payment method change to toggle fields appropriately
  if (paymentMethodField) {
    paymentMethodField.addEventListener("change", toggleFields);
    toggleFields(); // Initial toggle based on the default selected value
  }

  /**
   * Validate form fields to ensure they are filled correctly.
   * @returns {boolean} - Returns true if all form fields are valid, otherwise false.
   */
  function validateForm() {
    let valid = true;
    paymentForm.querySelectorAll("input").forEach(function (input) {
      if (!input.checkValidity()) {
        valid = false;
      }
    });
    return valid;
  }

  // Add event listener for Paystack button to handle the payment process
  if (paystackBtn) {
    paystackBtn.addEventListener("click", function (e) {
      if (!validateForm()) {
        paymentForm.reportValidity(); // Show validation errors if form is invalid
        return;
      }

      // Prevent form submission
      e.preventDefault();

      // Initialize payment using Paystack Inline
      let handler = PaystackPop.setup({
        key: paystackPublicKey, // Paystack public key
        email: userEmail, // User email
        amount: accessKeyPrice * 100, // Convert price to Pesewas
        currency: "GHS",

        // Callback function for successful payment
        callback: function (response) {
          // Redirect to callback URL with payment reference
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
