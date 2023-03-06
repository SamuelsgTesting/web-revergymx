
// validacion login

$(document).ready(function() {

    $("#validar_logueo").validate({
      rules: {
        username : {
          required: true,
        },
        password: {
          required: true,
        },
     

      },
      messages : {
        username: {
            required: "Por favor ingrese su usuario!",
        },
        password: {
            required: "Por favor ingrese su contraseña!",
            // min: "la contraseña debe contener al menos 8 caracteres, una mayuscula y al menos 1 digito"
        }
      }
    });

    $("#validar_register").validate({
        rules: {
          username : {
            required: true,
          },
          password: {
            required: true,
          },
       
  
        },
        messages : {
          username: {
              required: "Por favor ingrese su usuario!",
          },
          password: {
              required: "Por favor ingrese su contraseña!",
              // min: "la contraseña debe contener al menos 8 caracteres, una mayuscula y al menos 1 digito"
          }
        }
      });
  
    
  });