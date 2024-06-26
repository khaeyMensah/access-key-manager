document.addEventListener("DOMContentLoaded", function () {
  // Toggle log visibility functionality
  const toggleLogButton = document.getElementById("toggle-log");
  const keyLog = document.getElementById("key-log");

  // Check if elements exist before adding event listeners
  if (toggleLogButton && keyLog) {
    toggleLogButton.addEventListener("click", function () {
      if (keyLog.style.maxHeight) {
        keyLog.style.maxHeight = null;
        toggleLogButton.textContent = "View Logs";
      } else {
        keyLog.style.maxHeight = keyLog.scrollHeight + "px";
        toggleLogButton.textContent = "Hide Logs";
      }
    });
  }
});
