import React, { useState } from 'react';
import { fileAPI } from '../utils/api';

const FileUpload = ({ onUploadSuccess, appointmentId = null }) => {
  const [file, setFile] = useState(null);
  const [description, setDescription] = useState('');
  const [isPublic, setIsPublic] = useState('private');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size exceeds 10MB limit');
        setFile(null);
      } else {
        setFile(selectedFile);
        setError('');
      }
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('description', description);
      formData.append('is_public', isPublic);
      if (appointmentId) {
        formData.append('appointment_id', appointmentId);
      }

      await fileAPI.upload(formData);
      setSuccess('File uploaded successfully');
      setFile(null);
      setDescription('');
      setIsPublic('private');
      setTimeout(() => setSuccess(''), 3000);
      onUploadSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3>Upload File</h3>
      </div>

      {error && <div className="alert error">{error}</div>}
      {success && <div className="alert success">{success}</div>}

      <form onSubmit={handleUpload}>
        <div className="form-group">
          <label>Select File</label>
          <input
            type="file"
            onChange={handleFileChange}
            accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.txt"
          />
          <p style={{ fontSize: '12px', color: '#999' }}>
            Allowed: PDF, JPG, PNG, DOC, DOCX, TXT (Max 10MB)
          </p>
        </div>

        <div className="form-group">
          <label>Description (optional)</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the file..."
            rows="2"
          />
        </div>

        <div className="form-group">
          <label>Visibility</label>
          <select
            value={isPublic}
            onChange={(e) => setIsPublic(e.target.value)}
          >
            <option value="private">Private</option>
            <option value="shared-with-doctor">Shared with Doctor</option>
          </select>
        </div>

        <button type="submit" disabled={uploading || !file}>
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </form>
    </div>
  );
};

export default FileUpload;
