function toggleInputFields() {
  const modType = document.getElementById("modulationType").value;

  // Get groups
  const analogGroups = document.querySelectorAll(".analogInputs");
  const digitalGroup = document.querySelector(".digitalInputs");

  // Get all inputs
  const analogInputs = document.querySelectorAll(
    ".analogInputs input, .analogInputs select"
  );
  const digitalInput = document.querySelector(".digitalInputs input");

  // Common inputs (outside analog/digital groups)
  const carrierInputs = document.querySelectorAll(
    "input[name='carrierFrequency'], input[name='carrierAmplitude'], select[name='carrierWaveform']"
  );

  // Disable all inputs by default
  [...analogInputs, digitalInput, ...carrierInputs].forEach((input) => {
    if (input) input.disabled = true;
  });

  // Show/hide groups visually
  analogGroups.forEach((group) => {
    group.style.display = "none";
  });
  if (digitalGroup) digitalGroup.style.display = "none";

  // If modulation type is selected, enable and show appropriate inputs
  if (["AM", "FM", "PM", "DSBSC", "SSB"].includes(modType)) {
    analogInputs.forEach((input) => (input.disabled = false));
    carrierInputs.forEach((input) => (input.disabled = false));
    analogGroups.forEach((group) => (group.style.display = "block"));
  } else if (["ASK", "FSK", "QPSK", "BPSK"].includes(modType)) {
    if (digitalInput) {
      digitalInput.disabled = false;
      if (modType === "QPSK" && !digitalInput.value) {
        digitalInput.value = Array.from({ length: 8 }, () =>
          Math.random() > 0.5 ? 1 : 0
        ).join("");
      }
    }
    carrierInputs.forEach((input) => (input.disabled = false));
    if (digitalGroup) digitalGroup.style.display = "block";
  }
}

// Disable inputs on initial load
window.addEventListener("DOMContentLoaded", toggleInputFields);
