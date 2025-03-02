document.addEventListener("DOMContentLoaded", function () {
  const formInput = document.getElementById("email-input");
  const submitButton = document.getElementById("create-account");

  const API_URL =
    "https://canvas.instructure.com/api/v1/accounts/{account_id}/users"; // Replace with the actual account ID and Canvas URL
  const ACCESS_TOKEN = "YOUR_CANVAS_API_ACCESS_TOKEN"; // Replace with your Canvas API Access Token

  // Function to validate email format
  function validateEmail(email) {
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailPattern.test(email);
  }

  // Function to POST email to Canvas API
  function postEmailToCanvas(email) {
    fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${ACCESS_TOKEN}`,
      },
      body: JSON.stringify({
        user: {
          email: email,
          name: email.split("@")[0], // You can modify the name as needed
          login_id: email, // Set login_id to the email for login
        },
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.id) {
          alert("Account created successfully for " + email);
          console.log("Canvas Response:", data);
        } else {
          alert("There was an issue creating the account on Canvas.");
          console.log("Error Response:", data);
        }
      })
      .catch((error) => {
        alert("Error with Canvas API request.");
        console.error("Error:", error);
      });
  }

  // Event listener for submitting email
  submitButton.addEventListener("click", function () {
    const email = formInput.value.trim();

    if (validateEmail(email)) {
      postEmailToCanvas(email);
    } else {
      alert("Please enter a valid email address.");
    }
  });
});
