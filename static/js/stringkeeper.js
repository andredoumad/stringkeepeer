
$(document).ready(function(){
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




  //auto search
  var searchForm = $(".search-form")
  var searchInput = searchForm.find("[name='q']") // input name = 'q'
  var typingTimer;
  var typingInterval = 333
  var searchBtn = searchForm.find("[type='submit']")

  searchInput.keyup(function(event){
    console.log(searchInput.val())
    clearTimeout(typingTimer)
    typingTimer = setTimeout(performSearch, typingInterval)
  })

  searchInput.keydown(function(event){
    console.log(searchInput.val())
    clearTimeout(typingTimer)
  })


  function displaySearching(){
    searchBtn.addClass("disabled")
    searchBtn.html("<i class='fa fa-spin fa-spinner'></i> Searching...")
  }

  function performSearch(){
    displaySearching()

    var query = searchInput.val()

    setTimeout(function(){
      window.location.href='/search/?q=' + query
    }, 200)


  }

  //cart = add products

  var subscriptionForm = $(".form-subscription-ajax")

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

            submitSpan.html("<div class='btn-group'> <a class='btn btn-link' href='/cart/'>In cart</a> <button type='submit' class='btn btn-link'>Remove?</button></div>")
          }else{
            submitSpan.html("<button type='submit' class='btn btn-success'>Add</button>")
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
