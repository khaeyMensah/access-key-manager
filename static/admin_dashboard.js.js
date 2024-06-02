// document.getElementById("toggle-log-button").onclick = function () {
//   var logDropdown = document.getElementById("audit-log-dropdown");
//   if (logDropdown.style.display === "none") {
//     logDropdown.style.display = "block";
//   } else {
//     logDropdown.style.display = "none";
//   }
// };

// document.getElementById("toggle-log").addEventListener("click", function () {
//   var logDiv = document.getElementById("audit-log");
//   if (logDiv.style.display === "none") {
//     logDiv.style.display = "block";
//   } else {
//     logDiv.style.display = "none";
//   }
// });

// admin_dashboard.js

document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("toggle-log").addEventListener("click", function () {
    var logDiv = document.getElementById("audit-log");
    if (logDiv.style.display === "none") {
      logDiv.style.display = "block";
    } else {
      logDiv.style.display = "none";
    }
  });
});
