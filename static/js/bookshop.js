/**
 * BookVerse Online Bookshop — Real-Time Search & Cart Management (JavaScript + jQuery + AJAX)
 */
$(document).ready(function () {
  const $searchInput = $("#live-search-input");
  const $searchDropdown = $("#live-search-results");
  let debounceTimer = null;

  function showToast(message) {
    $("#cart-toast-body").text(message);
    const toastEl = document.getElementById("cart-toast");
    if (toastEl) {
      const toast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay: 2400 });
      toast.show();
    }
  }

  // 1. Real-Time Search Bar using JavaScript, jQuery & AJAX
  $searchInput.on("input", function () {
    const query = $(this).val().trim();
    clearTimeout(debounceTimer);

    if (query.length < 1) {
      $searchDropdown.hide().empty();
      return;
    }

    debounceTimer = setTimeout(function () {
      $.ajax({
        url: "/api/search",
        method: "GET",
        data: { q: query },
        dataType: "json",
        success: function (response) {
          $searchDropdown.empty();
          if (!response.books || response.books.length === 0) {
            $searchDropdown.append(
              `<div class="p-3 text-secondary small text-center">No books found matching "<strong>${$("<div>").text(query).html()}</strong>"</div>`
            );
          } else {
            response.books.slice(0, 6).forEach(function (b) {
              const safeTitle = $("<div>").text(b.title).html();
              const safeAuthor = $("<div>").text(b.author).html();
              const itemHtml = `
                <a href="${b.detail_url}" class="d-flex align-items-center justify-content-between p-2 px-3 text-decoration-none text-dark border-bottom">
                  <div class="me-2 text-truncate">
                    <div class="fw-semibold small text-truncate">${safeTitle}</div>
                    <div class="text-secondary" style="font-size: 0.75rem;">${safeAuthor} &bull; <span class="text-primary">${b.category}</span></div>
                  </div>
                  <span class="badge bg-primary-subtle text-primary fw-bold">&#8377;${b.price.toFixed(0)}</span>
                </a>
              `;
              $searchDropdown.append(itemHtml);
            });
          }
          $searchDropdown.show();
        }
      });
    }, 180);
  });

  // Hide search dropdown when clicking outside
  $(document).on("click", function (e) {
    if (!$(e.target).closest("#live-search-input, #live-search-results").length) {
      $searchDropdown.hide();
    }
  });

  // 2. Real-Time Add to Cart via AJAX
  $(document).on("click", ".btn-add-cart", function (e) {
    e.preventDefault();
    const bookId = $(this).data("book-id");
    const qty = $(this).data("qty") || 1;
    const $btn = $(this);
    const origHtml = $btn.html();

    $btn.prop("disabled", true).html('<span class="spinner-border spinner-border-sm me-1"></span>Adding...');

    $.ajax({
      url: "/api/cart/add",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ book_id: bookId, quantity: qty }),
      success: function (res) {
        if (res.success) {
          $("#nav-cart-badge").text(res.cart.total_quantity);
          showToast(res.message);
        }
      },
      error: function (xhr) {
        if (xhr.status === 401 && xhr.responseJSON && xhr.responseJSON.redirect) {
          window.location.href = xhr.responseJSON.redirect;
        } else {
          showToast("Please log in to add books to your cart.");
        }
      },
      complete: function () {
        $btn.prop("disabled", false).html(origHtml);
      }
    });
  });

  // 3. Real-Time Cart Quantity Update via AJAX
  $(document).on("click", ".btn-qty-change", function () {
    const bookId = $(this).data("book-id");
    const delta = parseInt($(this).data("delta"), 10);
    const $row = $(`#cart-row-${bookId}`);
    const $qtyInput = $row.find(".cart-qty-input");
    const currentQty = parseInt($qtyInput.val(), 10) || 1;
    const newQty = currentQty + delta;

    updateCartItemAjax(bookId, newQty);
  });

  // 4. Real-Time Cart Item Removal via AJAX
  $(document).on("click", ".btn-remove-cart", function () {
    const bookId = $(this).data("book-id");
    $.ajax({
      url: "/api/cart/remove",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ book_id: bookId }),
      success: function (res) {
        if (res.success) {
          refreshCartDOM(res.cart);
          showToast("Item removed from cart.");
        }
      }
    });
  });

  function updateCartItemAjax(bookId, newQty) {
    $.ajax({
      url: "/api/cart/update",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ book_id: bookId, quantity: newQty }),
      success: function (res) {
        if (res.success) {
          refreshCartDOM(res.cart);
        }
      }
    });
  }

  function refreshCartDOM(cart) {
    $("#nav-cart-badge").text(cart.total_quantity);
    if (cart.items.length === 0) {
      window.location.reload();
      return;
    }

    const activeIds = new Set();
    cart.items.forEach(function (item) {
      activeIds.add(item.book_id);
      const $row = $(`#cart-row-${item.book_id}`);
      if ($row.length) {
        $row.find(".cart-qty-input").val(item.quantity);
        $row.find(".cart-item-subtotal").html(`&#8377;${item.item_total.toFixed(2)}`);
      }
    });

    $("[id^='cart-row-']").each(function () {
      const rowId = parseInt($(this).attr("id").replace("cart-row-", ""), 10);
      if (!activeIds.has(rowId)) {
        $(this).fadeOut(200, function () { $(this).remove(); });
      }
    });

    $("#cart-subtotal").html(`&#8377;${cart.subtotal.toFixed(2)}`);
    $("#cart-tax").html(`&#8377;${cart.tax.toFixed(2)}`);
    $("#cart-grand-total").html(`&#8377;${cart.grand_total.toFixed(2)}`);
    $("#cart-total-qty").text(cart.total_quantity);
  }
});
