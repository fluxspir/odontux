    function clear_address_form() {
      document.getElementById('street').value=("");
      document.getElementById('district').value("");
      document.getElementById('city').value("");
      document.getElementById('state').value("");
      document.getElementById('country').value("");
    }
    function my_callback_br(content) {
      if (!("erro" in content)) {
        document.getElementById('street').value=(content.logradouro);
        document.getElementById('district').value=(content.bairro);
        document.getElementById('city').value=(content.localidade);
        document.getElementById('state').value=(content.uf);
        document.getElementById('country').value=('br');
      }
      else {
        clear_address_form();
        alert("CEP não encontrado")
      }
    }
    
    function get_content_br(valor) {

      var cep = valor.replace(/\D/g, '');

      if (cep != "") {

        var validacep = /^[0-9]{8}$/;
        
        if (validacep.test(cep)) {
          document.getElementById('street').value="...";

          //Cria um elemento javascript.
          var script = document.createElement('script');

          //Sincroniza com o callback.
          script.src = 'http://viacep.com.br/ws/'+ cep + '/json/?callback=my_callback_br';

          //Insere script no documento e carrega o conteúdo.
          document.body.appendChild(script);

        } else {
          // invalid cep
          clear_address_form();
          alert("Formato de CEP inválido")
        }

      } else {
        // CEP sem valor
        clear_address_form();
      }
    }
