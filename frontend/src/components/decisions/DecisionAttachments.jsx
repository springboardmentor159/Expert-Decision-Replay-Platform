import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Paperclip, Upload, Download, Trash2, File, FileText, CheckCircle2 } from 'lucide-react';
import { attachmentsApi } from '../../api/attachments';
import { useNotification } from '../../context/NotificationContext';
import { LoadingSpinner } from '../common/LoadingSpinner';

export function DecisionAttachments({ decisionId, canUpload = true }) {
  const [attachments, setAttachments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);
  const { success, error } = useNotification();

  const loadAttachments = useCallback(async () => {
    try {
      const data = await attachmentsApi.getDecisionAttachments(decisionId);
      setAttachments(data || []);
    } catch (err) {
      console.error('Failed to load attachments', err);
    } finally {
      setLoading(false);
    }
  }, [decisionId]);

  useEffect(() => {
    loadAttachments();
  }, [loadAttachments]);

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Max 25MB check
    if (file.size > 25 * 1024 * 1024) {
      error('File size exceeds 25MB limit.');
      return;
    }

    setUploading(true);
    try {
      await attachmentsApi.uploadAttachment(decisionId, file);
      success(`File "${file.name}" uploaded successfully.`);
      if (fileInputRef.current) fileInputRef.current.value = '';
      await loadAttachments();
    } catch (err) {
      error(err.message || 'Failed to upload attachment.');
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (att) => {
    try {
      const blob = await attachmentsApi.downloadAttachmentBlob(att.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = att.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      error('Failed to download file.');
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete "${name}"?`)) return;
    try {
      await attachmentsApi.deleteAttachment(id);
      success(`File "${name}" deleted.`);
      setAttachments(prev => prev.filter(a => a.id !== id));
    } catch (err) {
      error(err.message || 'Failed to delete attachment.');
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-color)',
      borderRadius: '12px',
      padding: '1.5rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
            <Paperclip size={18} style={{ color: 'var(--primary)' }} />
            Attached Documents & Specs
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: '0.2rem 0 0' }}>
            Architecture diagrams, benchmarks, and specification files supporting this decision.
          </p>
        </div>

        {canUpload && (
          <div>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              style={{ display: 'none' }}
              id="file-upload-input"
            />
            <button
              className="btn btn-primary btn-sm"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
            >
              <Upload size={15} />
              <span>{uploading ? 'Uploading...' : 'Upload Document'}</span>
            </button>
          </div>
        )}
      </div>

      {loading ? (
        <LoadingSpinner message="Loading attachments..." size="small" />
      ) : attachments.length === 0 ? (
        <div style={{
          border: '2px dashed var(--border-color)',
          borderRadius: '8px',
          padding: '2rem',
          textAlign: 'center',
          color: 'var(--text-muted)',
          fontSize: '0.85rem',
        }}>
          <Paperclip size={24} style={{ opacity: 0.4, margin: '0 auto 0.5rem' }} />
          No documents attached to this decision yet.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '0.75rem' }}>
          {attachments.map((att) => (
            <div
              key={att.id}
              style={{
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '0.75rem 1rem',
                background: 'var(--bg-card-solid, var(--bg-card))',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '0.5rem',
                transition: 'border-color 0.15s',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', minWidth: 0 }}>
                <FileText size={20} style={{ color: 'var(--primary)', flexShrink: 0 }} />
                <div style={{ minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: '0.85rem',
                      fontWeight: 600,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                    title={att.filename}
                  >
                    {att.filename}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    {formatFileSize(att.file_size)} • {new Date(att.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', flexShrink: 0 }}>
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => handleDownload(att)}
                  style={{ padding: '4px 8px' }}
                  title="Download file"
                >
                  <Download size={14} />
                </button>
                {canUpload && (
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => handleDelete(att.id, att.filename)}
                    style={{ padding: '4px 8px', color: 'var(--danger)' }}
                    title="Delete file"
                  >
                    <Trash2 size={14} />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
