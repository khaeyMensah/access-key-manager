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
