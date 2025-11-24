"""
Service de gestion du stockage Cloud (AWS S3)
"""
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from typing import Optional, BinaryIO
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class S3StorageService:
    """Service pour gérer le stockage des fichiers sur AWS S3"""
    
    def __init__(self):
        """Initialise le client S3"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.bucket_name = settings.AWS_BUCKET_NAME
            logger.info(f"✅ S3 Client initialisé : {self.bucket_name} ({settings.AWS_REGION})")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation S3 : {e}")
            raise
    
    def upload_file(self, file_content: bytes, file_name: str) -> Optional[str]:
        """
        Upload un fichier vers S3
        
        Args:
            file_content: Contenu du fichier en bytes
            file_name: Nom du fichier (ex: "data.csv")
            
        Returns:
            S3 key (chemin du fichier dans S3) ou None si erreur
        """
        try:
            # Générer un key unique avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"batch_uploads/{timestamp}_{file_name}"
            
            # Upload vers S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType='text/csv',
                Metadata={
                    'original_filename': file_name,
                    'upload_timestamp': timestamp
                }
            )
            
            logger.info(f"✅ Fichier uploadé vers S3 : {s3_key}")
            return s3_key
            
        except ClientError as e:
            logger.error(f"❌ Erreur upload S3 : {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur inattendue upload S3 : {e}")
            return None
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """
        Génère une URL signée pour télécharger un fichier depuis S3
        
        Args:
            s3_key: Chemin du fichier dans S3 (ex: "batch_uploads/20251111_143025_data.csv")
            expiration: Durée de validité de l'URL en secondes (défaut: 1h)
            
        Returns:
            URL signée ou None si erreur
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            logger.info(f"✅ URL présignée générée pour : {s3_key}")
            return url
            
        except ClientError as e:
            logger.error(f"❌ Erreur génération URL présignée : {e}")
            return None
    
    def delete_file(self, s3_key: str) -> bool:
        """
        Supprime un fichier de S3
        
        Args:
            s3_key: Chemin du fichier dans S3
            
        Returns:
            True si succès, False si erreur
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"✅ Fichier supprimé de S3 : {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Erreur suppression S3 : {e}")
            return False
    
    def list_files(self, prefix: str = "batch_uploads/") -> list:
        """
        Liste les fichiers dans S3
        
        Args:
            prefix: Préfixe pour filtrer les fichiers (ex: "batch_uploads/")
            
        Returns:
            Liste des fichiers avec métadonnées
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            files = []
            for obj in response['Contents']:
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'filename': obj['Key'].split('/')[-1]
                })
            
            logger.info(f"✅ {len(files)} fichiers trouvés dans S3")
            return files
            
        except ClientError as e:
            logger.error(f"❌ Erreur listing S3 : {e}")
            return []
    
    def check_file_exists(self, s3_key: str) -> bool:
        """
        Vérifie si un fichier existe dans S3
        
        Args:
            s3_key: Chemin du fichier dans S3
            
        Returns:
            True si existe, False sinon
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError:
            return False


# Instance globale du service
s3_service = S3StorageService() if settings.USE_S3_STORAGE else None