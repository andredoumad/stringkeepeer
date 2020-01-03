$(document).ready(function(){


// Stripe Form START 
var stripeFormModule = $(".stripe-payment-form-module")
var stripeModuleToken = stripeFormModule.attr("data-token")
var stripeModuleNextUrl = stripeFormModule.attr("data-next-url")
var stripeModuleBtnTitle = stripeFormModule.attr('data-btn-title') || 'Add card'
var stripeTemplate = $.templates("#stripeTemplate")
var stripeTemplateDataContext = {
    publishKey: stripeModuleToken,
    nextUrl: stripeModuleNextUrl,
    btnTitle: stripeModuleBtnTitle
}
var stripeTemplateHtml = stripeTemplate.render(stripeTemplateDataContext)
stripeFormModule.html(stripeTemplateHtml)

// https secure site when live

var paymentForm = $(".stripe-payment-form")


if (paymentForm.length > 1){
    alert('only one payment for is allowed per page')
    paymentForm.css('display', 'none')
}
else if (paymentForm.length == 1){

var pubKey = paymentForm.attr('data-token')
var nextUrl = paymentForm.attr('data-next-url')

// Create a Stripe client.
var stripe = Stripe('pk_test_k8LAxPXmWxonT6ZUDVxjsuzL00LCGJ2rLX');

// Create an instance of Elements.
var elements = stripe.elements();

// Custom styling can be passed to options when creating an Element.
// (Note that this demo uses a wider set of styles than the guide below.)
var style = {
    base: {
    color: '#32325d',
    fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
    fontSmoothing: 'antialiased',
    fontSize: '16px',
    '::placeholder': {
        color: '#aab7c4'
    }
    },
    invalid: {
    color: '#fa755a',
    iconColor: '#fa755a'
    }
};

// Create an instance of the card Element.
var card = elements.create('card', {style: style});

// Add an instance of the card Element into the `card-element` <div>.
card.mount('#card-element');

// Handle real-time validation errors from the card Element.
card.addEventListener('change', function(event) {
    var displayError = document.getElementById('card-errors');
    if (event.error) {
    displayError.textContent = event.error.message;
    } else {
    displayError.textContent = '';
    }
});

// Handle form submission.
var form = document.getElementById('stripe-payment-form');
form.addEventListener('submit', function(event) {
    event.preventDefault();

    stripe.createToken(card).then(function(result) {
    if (result.error) {
        // Inform the user if there was an error.
        var errorElement = document.getElementById('card-errors');
        errorElement.textContent = result.error.message;
    } else {
        // Send the token to your server.
        stripeTokenHandler(nextUrl, result.token);
        card.clear()
    }
    });
});



function redirectToNext(nextPath, timeoffset){
    console.log('timeoffset: ' + timeoffset)
    console.log('nextPath: ' + nextPath)
    if (nextPath){
        setTimeout(function(){
            console.log('timeoffset: ' + timeoffset)
            console.log('nextPath: ' + nextPath)
                window.location.href = nextPath
            }, timeoffset)
    }
}


// Submit the form with the token ID.
function stripeTokenHandler(nextUrl, token) {
    console.log('token ID: ' + token.id)
    var paymentMethodEndpoint = '/billing/payment-method/create/'
    var data = {
        'token': token.id
    }
    $.ajax({
        data: data,
        url: paymentMethodEndpoint,
        method: "POST",
        success: function(data){
            var successMsg = data.message || "success, your card was added !"
            card.clear()
            if (nextUrl){
                successMsg = successMsg + "<br/><br/><i class='fa fa-spin fa-spinner'></i>Redirecting..."
            }
            if ($.alert){ // if alert library is installed use it, 
                $.alert(successMsg)
            } else { // otherwise use this.
                alert(successMsg)
            }
            redirectToNext(nextUrl, 1500)
        },
        error: function(error){
            console.log(error)
        }
    })
    // // Insert the token ID into the form so it gets submitted to the server
    // var form = document.getElementById('stripe-payment-form');
    // var hiddenInput = document.createElement('input');
    // hiddenInput.setAttribute('type', 'hidden');
    // hiddenInput.setAttribute('name', 'stripeToken');
    // hiddenInput.setAttribute('value', token.id);
    // form.appendChild(hiddenInput);

    // // Submit the form
    // form.submit();
}
}
// _stripe_ form end

})