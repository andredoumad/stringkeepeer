


$(document).ready(function(){

    var button = document.querySelector('#submit-button');
    var form = document.querySelector('#payment-form');
    var testvariable = 'emptytestvariable';
    var nonce = 'emptynonce';
    var gordon = 'emptygordon';
    var payload_nonce;
  
    braintree.dropin.create({
  
      authorization: '{{ client_token }}',
      container: '#dropin-container',
      card: {
      cardholderName: { required: true },
      overrides: {
        styles: {
  
          input: {
            color: 'blue',
            'font-size': '18px'
          },
          '.number': {
            'font-family': 'monospace'
            // Custom web fonts are not supported. Only use system installed fonts.
          },
          '.invalid': {
            color: 'red'
          }
        }
      }
    }
  }, function (createErr, instance) {
      button.addEventListener('click', function () {
        document.querySelector('#testvariable').value = 'hello from javascript'
        console.log("document.querySelector('#testvariable').value: " + document.querySelector('#testvariable').value)
        document.querySelector('#gordon').value = 'hello gordon from javascript'
        console.log("document.querySelector('#gordon').value: " + document.querySelector('#gordon').value)
  
        function updateGordon(gordon_update_value){ 
            console.log('updateGordon function: ' + gordon_update_value)
            document.querySelector('#gordon').value = gordon_update_value
            console.log("document.querySelector('#gordon').value: " + document.querySelector('#gordon').value)
            document.querySelector('#testvariable').value = 'hello from updategordon'
            document.querySelector('#gordon').value = 'hello gordon freeman'
        }
        instance.requestPaymentMethod(function (requestPaymentMethodErr, payload) {
          // When the user clicks on the 'Submit payment' button this code will send the
          // encrypted payment information in a variable called a payment method nonce
  
          document.querySelector('#nonce').value = payload.nonce
          console.log('payment method nonce is: ' + payload.nonce)
          $('#nonce').val(payload.nonce);
          $('#gordon').val(payload.nonce);
          gordon = payload.nonce
          
          updateGordon(payload.nonce)
          // console.log('gordon is: ' + gordon)
          // document.querySelector('#gordon').value = payload.nonce
          nonce = payload.nonce
          console.log('nonce A: ' + document.querySelector('#nonce').value)
          
          console.log('HELLO')
          $.ajax({
            type: 'POST',
            url: '/cart/checkout/success/',
            data: {'paymentMethodNonce': payload.nonce}
          }).done(function(result) {
            console.log('nonce B: ' + document.querySelector('#nonce').value)
            // Tear down the Drop-in UI
            instance.teardown(function (teardownErr) {
              console.log('nonce C: ' + document.querySelector('#nonce').value)
  
              if (teardownErr) {
                console.error('Could not tear down Drop-in UI!');
              } else {
                console.log('nonce D: ' + document.querySelector('#nonce').value)
                console.info('Drop-in UI has been torn down!');
                // Remove the 'Submit payment' button
                $('#submit-button').remove();
              }
            });
            console.log('nonce E: ' + document.querySelector('#nonce').value)
            if (result.success) {
              console.log('nonce F: ' + document.querySelector('#nonce').value)
              $('#nonce').value(nonce)
              $('#checkout-message').html('<h1>Success</h1><p>Your Drop-in UI is working! Check your <a href="https://sandbox.braintreegateway.com/login">sandbox Control Panel</a> for your test transactions.</p><p>Refresh to try another transaction.</p>');
            } else {
              console.log(result);
              $('#checkout-message').html('<h1>Error</h1><p>Check your console.</p>');
            }
            console.log('nonce G: ' + document.querySelector('#nonce').value)
            gordon = document.querySelector('#nonce').value
            console.log('gordon final: ' + gordon)
            payload_nonce = gordon
            console.log('payload_nonce A: ' + payload_nonce)
            document.querySelector('#testvariable').value = payload_nonce
  
            console.log("document.querySelector('#remove-subscription-field-id').value: " + document.querySelector('#remove-subscription-field-id'))
            console.log("document.querySelector('#remove-subscription-field-name').value: " + document.querySelector('#remove-subscription-field-name'))
            form.submit()
          })
  
        })
      })
    })





    function RemoveSubscription(subscription) {
        console.log('RemoveSubscription')
          $.ajax({
              url : '.',
              type : "POST",
              data : { removeSubscription : subscription }
          }).done(function(returned_data){
            console.log('returned_data: ' + JSON.stringify(returned_data))
              // This is the ajax.done() method, where you can fire events after the ajax method is complete 
      
              // For instance, you could hide/display your add/remove button here
      
          });
      }


})