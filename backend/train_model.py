from fine_tuning import FineTuningManager
import os
from dotenv import load_dotenv

def train_model():
    """Train the fine-tuned model using the prepared data"""
    # Load environment variables
    load_dotenv()
    
    # Initialize the fine-tuning manager
    ft_manager = FineTuningManager()
    
    try:
        # Create training file
        ft_manager.create_training_file("training_data.jsonl")
        
        # Upload the file
        print("Uploading training file...")
        file_id = ft_manager.upload_training_file("training_data.jsonl")
        print(f"File uploaded successfully. File ID: {file_id}")
        
        # Create fine-tuning job
        print("Creating fine-tuning job...")
        job_id = ft_manager.create_fine_tuning_job(file_id)
        print(f"Fine-tuning job created successfully. Job ID: {job_id}")
        
        # Monitor the training progress
        while True:
            status = ft_manager.get_fine_tuning_status(job_id)
            print(f"Training status: {status['status']}")
            
            if status['status'] == 'succeeded':
                print(f"Training completed successfully!")
                print(f"Fine-tuned model ID: {status['fine_tuned_model']}")
                print(f"Trained tokens: {status['trained_tokens']}")
                break
            elif status['status'] == 'failed':
                print(f"Training failed: {status['error']}")
                break
            elif status['status'] == 'cancelled':
                print("Training was cancelled")
                break
            
            # Wait for 60 seconds before checking again
            import time
            time.sleep(60)
            
    except Exception as e:
        print(f"An error occurred during training: {str(e)}")

if __name__ == "__main__":
    train_model() 