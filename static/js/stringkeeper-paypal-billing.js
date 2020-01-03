$(document).ready(function(){

    
var paypalFormModule = $(".paypal-payment-form-module")
var paypalModuleToken = paypalFormModule.attr("data-token")
var paypalModuleNextUrl = paypalFormModule.attr("data-next-url")
var paypalModuleBtnTitle = paypalFormModule.attr('data-btn-title') || 'Add card'
var paypalTemplate = $.templates("#paypalTemplate")
var paypalTemplateDataContext = {
    publishKey: paypalModuleToken,
    nextUrl: paypalModuleNextUrl,
    btnTitle: paypalModuleBtnTitle,
}
var paypalTemplateHtml = paypalTemplate.render(paypalTemplateDataContext)
// https secure site when live

var paymentForm = $(".paypal-payment-form")

paypalFormModule.html(paypalTemplateHtml)



var pubKey = paymentForm.attr('data-token')
var nextUrl = paymentForm.attr('data-next-url')

var form = document.getElementById('paypal-payment-form');

paypal.Buttons({

    style: {
      layout:  'vertical',
      color:   'blue',
      shape:   'rect',
      label:   'paypal'

    },
    
    createOrder: function(data, actions) {
    // This function sets up the details of the transaction, including the amount and line item details.
    
    return actions.order.create({
        purchase_units: [{
        amount: {
            value: '0.01'
        }
        }]
    });
  }
  }).render('#paypal-button-container');

})