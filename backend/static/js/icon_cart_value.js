$(document).ready(function () {
    var cartValue = $('.icon-cart').data('cart-value');

        if (cartValue > 0) {
            $('.icon-cart')
                .append('<style>.icon-cart::before { opacity: 1; }</style>')
                .attr('data-cart-content', cartValue);
        }
});