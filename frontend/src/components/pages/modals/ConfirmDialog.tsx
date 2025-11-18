import React, { useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { Modal } from '../../ui/Modal';
import { Button } from '../../ui/Button';
import { Input } from '../../ui/Input';
import { Card, CardBody } from '../../ui/Card';

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void> | void;
  title: string;
  message: string;
  description?: string;
  confirmText?: string;
  cancelText?: string;
  danger?: boolean;
  requiresTyping?: boolean;
  typingPrompt?: string;
  requiresCheckbox?: boolean;
  checkboxLabel?: string;
  itemCount?: number;
  isLoading?: boolean;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  description,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  danger = false,
  requiresTyping = false,
  typingPrompt = 'type DELETE',
  requiresCheckbox = false,
  checkboxLabel = 'I understand this action cannot be undone',
  itemCount,
  isLoading = false,
}) => {
  const [typedValue, setTypedValue] = useState('');
  const [checkboxChecked, setCheckboxChecked] = useState(false);
  const isConfirmEnabled =
    (!requiresTyping || typedValue.toUpperCase() === 'DELETE') &&
    (!requiresCheckbox || checkboxChecked);

  const handleConfirm = async () => {
    await onConfirm();
    setTypedValue('');
    setCheckboxChecked(false);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm" showCloseButton={!isLoading}>
      <div className="space-y-4">
        {/* Warning Icon and Message */}
        <div className="flex items-start gap-3">
          {danger && <AlertCircle size={20} className="text-red-600 flex-shrink-0 mt-0.5" />}
          <div>
            <p className="font-semibold text-slate-900">{message}</p>
            {description && <p className="text-sm text-slate-600 mt-2">{description}</p>}
            {itemCount !== undefined && (
              <p className="text-sm font-medium text-slate-700 mt-2">
                This action will affect {itemCount} item{itemCount !== 1 ? 's' : ''}.
              </p>
            )}
          </div>
        </div>

        {/* Typing Confirmation */}
        {requiresTyping && (
          <Card className="border-red-200 bg-red-50">
            <CardBody>
              <p className="text-sm text-red-700 font-medium mb-2">This action is irreversible!</p>
              <Input
                placeholder={typingPrompt}
                value={typedValue}
                onChange={(e) => setTypedValue(e.target.value)}
                disabled={isLoading}
              />
              <p className="text-xs text-red-600 mt-2">
                Type <strong>DELETE</strong> to confirm
              </p>
            </CardBody>
          </Card>
        )}

        {/* Checkbox Confirmation */}
        {requiresCheckbox && (
          <Card className="border-red-200 bg-red-50">
            <CardBody>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={checkboxChecked}
                  onChange={(e) => setCheckboxChecked(e.target.checked)}
                  disabled={isLoading}
                  className="w-5 h-5 rounded border-2 border-slate-300 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:bg-slate-100 disabled:cursor-not-allowed cursor-pointer transition-colors duration-200"
                />
                <span className="text-sm font-medium text-red-700">{checkboxLabel}</span>
              </label>
            </CardBody>
          </Card>
        )}

        {/* Actions */}
        <div className="flex gap-3 pt-4 border-t border-slate-200">
          <Button variant="secondary" onClick={onClose} disabled={isLoading} className="flex-1">
            {cancelText}
          </Button>
          <Button
            variant={danger ? 'danger' : 'primary'}
            onClick={handleConfirm}
            disabled={!isConfirmEnabled || isLoading}
            isLoading={isLoading}
            className="flex-1"
          >
            {confirmText}
          </Button>
        </div>
      </div>
    </Modal>
  );
};
