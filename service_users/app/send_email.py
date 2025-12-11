import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

logger = logging.getLogger(__name__)

def send_otp_email(to_email: str, code: str):
    """Envoie un code OTP via SendGrid"""
    
    # Récupération des variables d'environnement
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("FROM_EMAIL")
    
    if not sendgrid_api_key:
        logger.error("❌ SENDGRID_API_KEY manquant dans les variables d'environnement")
        raise Exception("Configuration SendGrid manquante")
    
    if not from_email:
        logger.warning("⚠️ FROM_EMAIL non configuré, utilisation d'une valeur par défaut")
        from_email = "noreply@transport-urbain.ma"
    
    logger.info(f"📧 Envoi d'OTP à {to_email} depuis {from_email}")
    
    # Construction du contenu HTML
    html = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Code de vérification</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
          }}
          .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          }}
          .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
          }}
          .content {{
            padding: 30px;
          }}
          .code-container {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            padding: 25px;
            border-radius: 8px;
            letter-spacing: 8px;
            margin: 30px 0;
            font-family: 'Courier New', monospace;
          }}
          .expiration {{
            color: #666;
            text-align: center;
            font-size: 14px;
            margin-top: 20px;
          }}
          .footer {{
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            font-size: 12px;
            border-top: 1px solid #e9ecef;
          }}
          .warning {{
            background-color: #fff3cd;
            border: 1px solid #ffecb5;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            font-size: 14px;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1 style="margin: 0; font-size: 28px;">🔐 Code de vérification</h1>
            <p style="margin: 10px 0 0; opacity: 0.9;">Sécurisez votre accès</p>
          </div>
          
          <div class="content">
            <p>Bonjour,</p>
            <p>Voici votre code de vérification pour accéder à votre compte :</p>
            
            <div class="code-container">
              {code}
            </div>
            
            <div class="warning">
              <strong>⚠️ Important :</strong> Ne partagez jamais ce code avec qui que ce soit.
              Notre équipe ne vous demandera jamais votre code de vérification.
            </div>
            
            <p class="expiration">
              ⏱️ Ce code expirera dans <strong>5 minutes</strong>
            </p>
            
            <p>Si vous n'avez pas demandé ce code, veuillez ignorer cet email.</p>
          </div>
          
          <div class="footer">
            <p>© 2024 Transport Urbain. Tous droits réservés.</p>
            <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
          </div>
        </div>
      </body>
    </html>
    """
    
    # Version texte simple pour les clients email qui ne supportent pas HTML
    plain_text = f"""
    Code de vérification
    
    Voici votre code de vérification pour accéder à votre compte : {code}
    
    ⚠️ Important : Ne partagez jamais ce code avec qui que ce soit.
    Notre équipe ne vous demandera jamais votre code de vérification.
    
    ⏱️ Ce code expirera dans 5 minutes.
    
    Si vous n'avez pas demandé ce code, veuillez ignorer cet email.
    
    --
    Transport Urbain
    © 2024 Tous droits réservés.
    """
    
    try:
        # Création de l'objet Mail SendGrid
        message = Mail(
            from_email=Email(from_email),
            to_emails=To(to_email),
            subject="🔐 Votre code de connexion - Transport Urbain",
            plain_text_content=plain_text,
            html_content=html
        )
        
        # Envoi de l'email via SendGrid
        logger.info(f"🔗 Connexion à l'API SendGrid...")
        sg = SendGridAPIClient(sendgrid_api_key)
        
        logger.info("📤 Envoi du message via SendGrid...")
        response = sg.send(message)
        
        # Journalisation de la réponse
        logger.info(f"✅ Email envoyé avec succès à {to_email}")
        logger.info(f"📊 Status Code: {response.status_code}")
        logger.info(f"📊 Headers: {response.headers}")
        
        # Vérification du statut de l'envoi
        if response.status_code in [200, 202]:
            logger.info(f"🎯 Email délivré avec succès à {to_email}")
            return True
        else:
            logger.error(f"⚠️ Réponse inattendue de SendGrid: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'envoi via SendGrid: {str(e)}")
        
        # Messages d'erreur plus détaillés
        if "Unauthorized" in str(e):
            raise Exception("Erreur d'authentification SendGrid. Vérifiez votre clé API.")
        elif "Forbidden" in str(e):
            raise Exception("Accès refusé. Vérifiez les permissions de votre clé API.")
        else:
            raise Exception(f"Erreur lors de l'envoi: {str(e)}")