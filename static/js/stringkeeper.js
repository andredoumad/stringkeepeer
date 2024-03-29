
$(document).ready(function(){

  // $("#about-btn").click( function(event) {
  //   alert("You clicked the button using JQuery!");
  // });

  
  // Contact form handler

  var contactForm = $(".contact-form")
  var contactFormMethod = contactForm.attr("method")
  var contactFormEndpoint = contactForm.attr("action") // /abc/ 

  function displaySubmitting(submitBtn, defaultText, doSubmit){
    
    if (doSubmit){
      submitBtn.addClass("disabled")
      submitBtn.html("<i class='fa fa-spin fa-spinner'></i> Sending...")

    } else {
      submitBtn.removeClass("disabled")
      submitBtn.html(defaultText)
    }
  }


  contactForm.submit(function(event){
    event.preventDefault()

    var contactFormSubmitBtn = contactForm.find("[type='submit']")
    var contactFormSubmitBtnTxt = contactFormSubmitBtn.text()

    var contactFormData = contactForm.serialize()
    var thisForm = $(this)
    displaySubmitting(contactFormSubmitBtn, "", true)

    $.ajax({
      method: contactFormMethod,
      url: contactFormEndpoint,
      data: contactFormData,
      success: function(data){
        contactForm[0].reset()
        $.alert({
          title: "Success!",
          content: data.message,
          theme: 'modern'
        })
        setTimeout(function(){
          displaySubmitting(contactFormSubmitBtn, contactFormSubmitBtnTxt, false)
        }, 1000)
      },
      error: function(errorData){
        console.log(error.responseJSON)
        var jsonData = error.responseJSON
        var msg = ""

        $.each(jsonData, function(key, value){ // key, value instead of an array of index / object 
          msg += key + ": " + value[0].message + "</br>"

        })
        
        $.alert({
          title: "That was unexpected...",
          content: 'An error occured, please try again later...',
          theme: 'modern'
        })
        setTimeout(function(){
          displaySubmitting(contactFormSubmitBtn, contactFormSubmitBtnTxt, false)
        }, 1000)
      }
    })
  })






  // Cart + Add Subscriptions 
  var subscriptionForm = $(".form-subscription-ajax") // #form-subscription-ajax

  function getOwnedSubscription(subscriptionId, submitSpan){
    var actionEndpoint = '/orders/endpoint/verify/ownership/'
    var httpMethod = 'GET'
    var data = {
      subscription_id: subscriptionId
    }

    var isOwner;
    $.ajax({
        url: actionEndpoint,
        method: httpMethod,
        data: data,
        success: function(data){
          console.log(data)
          console.log(data.owner)
          if (data.owner){
            isOwner = true
            submitSpan.html("<a class='btn btn-warning' href='/library/'>In Library</a>")
          } else {
            isOwner = false
          }
        },
        error: function(erorr){
          console.log(error)

        }
    })
    return isOwner
    
  }

  $.each(subscriptionForm, function(index, object){
    var $this = $(this)
    var isUser = $this.attr("data-user")
    var submitSpan = $this.find(".submit-span")
    var subscriptionInput = $this.find("[name='subscription_id']")
    var subscriptionId = subscriptionInput.attr("value")
    var subscriptionIsDigital = subscriptionInput.attr("data-is-digital")
    
    if (subscriptionIsDigital && isUser){
      var isOwned = getOwnedSubscription(subscriptionId, submitSpan)
    }
  })  


  subscriptionForm.submit(function(event){
    event.preventDefault();
    //console.log('Form is not sending')
    var thisForm = $(this)
    //var actionEndpoint = thisForm.attr('action');
    var actionEndpoint = thisForm.attr('data-endpoint');
    var httpMethod = thisForm.attr('method');
    var formData = thisForm.serialize();

    $.ajax({
        url: actionEndpoint,
        method: httpMethod,
        data: formData,
        success: function(data){
          console.log('success')
          console.log('data: ' + data)
          console.log('Added: ', data.added)
          console.log('Removed: ', data.removed)
          var submitSpan = thisForm.find('.submit-span')
          if (data.added){
            // submitSpan.html("<button type='submit' class='btn btn-danger'>Remove</button>")
            //<div class='btn-group'> <a class='btn btn-link' href='/cart/'>In cart</a> <button type='submit' class='btn btn-link'>Remove?</button></div>

            submitSpan.html("<div class='btn-group'> <a class='btn btn-info btn-block' href='/cart/'>In Cart</a>")
          }else{
            submitSpan.html("<button type='submit' class='btn btn-success btn-block'>Subscribe</button>")
          }
          var navbarCount = $(".navbar-cart-count")
          navbarCount.text(data.cartItemCount)
          var currentPath = window.location.href

          if (currentPath.indexOf('cart') != -1){
            refreshCart()
          }

        },

        error: function(errorData){
          $.alert({
            title: "That was unexpected...",
            content: 'An error occured, please try again later...',
            theme: 'modern'
          })
          console.log('error')
          console.log(errorData)
        }
    })

  })
  
  function refreshCart(){
    console.log('in current cart')
    var cartTable = $('.cart-table')
    var cartBody = cartTable.find('.cart-body')
    //cartBody.html('<h1>Changed</h1>')
    var subscriptionRows = cartBody.find('.cart-subscription')
    var currentUrl = window.location.href

    var refreshCartUrl ='/api/cart/';
    var refreshCartMethod = 'GET';
    var data = {};
    $.ajax({
      url: refreshCartUrl,
      method: refreshCartMethod,
      data: data,
      success: function(data){

        console.log('success')
        console.log(data)
        var hiddenCartItemRemoveForm = $(".cart-item-remove-form")
        if (data.subscriptions.length > 0){
          subscriptionRows.html(" ")
          i = data.subscriptions.length
          $.each(data.subscriptions, function(index, value){
            console.log(value)

            var newCartItemRemove = hiddenCartItemRemoveForm.clone()
            console.log('newCartItemRemove = ' + newCartItemRemove)
            console.log('newCartItemRemove.html() = ' + newCartItemRemove.html())
            newCartItemRemove.css('display', 'block')
            // newCartItemRemove.removeClass('hidden-class')
            newCartItemRemove.find('.cart-item-subscription-id').val(value.id)
              cartBody.prepend("<tr><th scope=\"row\">" + i + "</th><td><a href='" + value.url + "'>" + value.title + "</a>" + newCartItemRemove.html() + "</td><td>" + value.price + "</td></tr>")
              i --                          
          })

          cartBody.find('.cart-subtotal').text(data.subtotal)
          cartBody.find('.cart-total').text(data.total)
          
        } else {
          window.location.href = currentUrl
          //cartBody.find('.cart-subtotal').text(data.subtotal)
          //cartBody.find('.cart-total').text(data.total)
        }

      },
      error: function(errorData){
        console.log('error')
        console.log(errorData)
        $.alert({
          title: "Oops!",
          content: "An error occurred",
          theme: "modern",
        })
      }
    })



  }

})
