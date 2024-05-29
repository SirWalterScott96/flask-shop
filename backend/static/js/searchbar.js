$(document).ready(function () {
  var allProducts = {};

  $.ajax({
    type: "GET",
    url: "/product/get-all-products",
    success: function (response) {
      allProducts = response;
    },
  });

  const resultSearchBox = $(".search-result-box");
  const inputBox = $(".input-box");

  inputBox.on("keyup", function () {
    let result = [];
    let input = inputBox.val().toLowerCase();
    if (input.length > 2) {
      result = Object.keys(allProducts).filter(function (key) {
        return key.toLowerCase().includes(input);
      });
    }
    displayResultBox(result);
  });

  function displayResultBox(result) {
    const content = result.map((list) => {
      return $("<li>").text(list);
    });

    resultSearchBox.empty();

    if (content.length > 0) {
      const ul = $("<ul>").append(content);
      resultSearchBox.append(ul);
    }
  }

  resultSearchBox.on("click", "li", function () {
    var selectedProduct = $(this).text();
    inputBox.val(selectedProduct);
    resultSearchBox.empty();
    $(".search-btn").click();
    console.log(1);
  });
});
