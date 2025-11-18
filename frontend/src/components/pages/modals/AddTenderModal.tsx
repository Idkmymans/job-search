import React, { useState } from 'react';
import { Plus, AlertCircle } from 'lucide-react';
import { Modal } from '../../ui/Modal';
import { Button } from '../../ui/Button';
import { Input, Textarea, Select } from '../../ui/Input';
import { Card, CardBody } from '../../ui/Card';
import { Tender } from '../../../types';
import { useNotification } from '../../../context/NotificationContext';

interface AddTenderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (tender: Omit<Tender, 'id' | 'created_at' | 'updated_at'>) => Promise<void>;
  isLoading?: boolean;
  existingIfbNumbers?: string[];
}

const PROCUREMENT_TYPES = [
  'works ncb',
  'goods ncb',
  'services ncb',
  'works',
  'goods',
  'services',
];

const PROVINCES = [
  'Not specified',
  'Bagmati',
  'Gandaki',
  'Lumbini',
  'Province 1',
  'Province 2',
];

export const AddTenderModal: React.FC<AddTenderModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  isLoading,
  existingIfbNumbers = [],
}) => {
  const { addNotification } = useNotification();
  const [errors, setErrors] = useState<Record<string, string>>({});

  const [formData, setFormData] = useState({
    ifb_no: '',
    title: '',
    organization: '',
    deadline: '',
    procurement_type: 'works ncb',
    notice_date: '',
    province: 'Not specified',
    source: 'Manual',
  });

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.ifb_no.trim()) newErrors.ifb_no = 'IFB No is required';
    if (existingIfbNumbers.includes(formData.ifb_no)) {
      newErrors.ifb_no = 'This IFB No already exists in the database';
    }

    if (!formData.title.trim()) newErrors.title = 'Title is required';
    if (!formData.organization.trim()) newErrors.organization = 'Organization is required';
    if (!formData.deadline) newErrors.deadline = 'Deadline is required';
    if (!formData.notice_date) newErrors.notice_date = 'Notice date is required';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      addNotification('error', 'Please fix the errors in the form');
      return;
    }

    try {
      const deadlineDate = new Date(formData.deadline);
      const noticeDate = new Date(formData.notice_date);
      const now = new Date();
      const daysLeft = Math.ceil((deadlineDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));

      const tenderData: Omit<Tender, 'id' | 'created_at' | 'updated_at'> = {
        ifb_no: formData.ifb_no.trim(),
        title: formData.title.trim(),
        organization: formData.organization.trim(),
        deadline: deadlineDate.toISOString(),
        procurement_type: formData.procurement_type,
        notice_date: noticeDate.toISOString(),
        province: formData.province,
        source: formData.source,
        days_left: Math.max(0, daysLeft),
        scraped_date: new Date().toISOString().split('T')[0],
        marked_relevant: false,
      };

      await onSubmit(tenderData);
      addNotification('success', 'Tender added successfully');
      setFormData({
        ifb_no: '',
        title: '',
        organization: '',
        deadline: '',
        procurement_type: 'works ncb',
        notice_date: '',
        province: 'Not specified',
        source: 'Manual',
      });
      setErrors({});
      onClose();
    } catch (error) {
      addNotification('error', 'Failed to add tender');
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add New Tender" size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Duplicate Warning */}
        {errors.ifb_no && errors.ifb_no.includes('already exists') && (
          <Card className="border-amber-200 bg-amber-50">
            <CardBody className="flex items-start gap-3 text-amber-800 text-sm">
              <AlertCircle size={18} className="flex-shrink-0 mt-0.5" />
              <div>{errors.ifb_no}</div>
            </CardBody>
          </Card>
        )}

        {/* IFB No and Title */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="IFB No"
            placeholder="e.g., bktmun/NCB/works/04/082/83"
            value={formData.ifb_no}
            onChange={(e) => setFormData({ ...formData, ifb_no: e.target.value })}
            error={errors.ifb_no}
            required
          />
          <Select
            label="Procurement Type"
            value={formData.procurement_type}
            onChange={(e) => setFormData({ ...formData, procurement_type: e.target.value })}
            options={PROCUREMENT_TYPES.map((type) => ({
              value: type,
              label: type.toUpperCase(),
            }))}
          />
        </div>

        {/* Title */}
        <Input
          label="Title"
          placeholder="Tender title"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          error={errors.title}
          required
        />

        {/* Organization and Province */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Organization"
            placeholder="Organization name"
            value={formData.organization}
            onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
            error={errors.organization}
            required
          />
          <Select
            label="Province"
            value={formData.province}
            onChange={(e) => setFormData({ ...formData, province: e.target.value })}
            options={PROVINCES.map((prov) => ({
              value: prov,
              label: prov,
            }))}
          />
        </div>

        {/* Dates */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Notice Date"
            type="datetime-local"
            value={formData.notice_date}
            onChange={(e) => setFormData({ ...formData, notice_date: e.target.value })}
            error={errors.notice_date}
            required
          />
          <Input
            label="Deadline"
            type="datetime-local"
            value={formData.deadline}
            onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
            error={errors.deadline}
            required
          />
        </div>

        {/* Source Info */}
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
          Source: {formData.source}
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4 border-t border-slate-200">
          <Button variant="secondary" onClick={onClose} className="flex-1">
            Cancel
          </Button>
          <Button variant="primary" type="submit" isLoading={isLoading} className="flex-1">
            Add Tender
          </Button>
        </div>
      </form>
    </Modal>
  );
};
