import { useState, useEffect } from 'react'
import { PencilRuler, FloppyDisk, ArrowsClockwise } from '@phosphor-icons/react'
import { Modal, Input, Button } from '../shared'

export default function EditStudentModal({ isOpen, onClose, student, onSave }) {
  const [formData, setFormData] = useState({
    id_number: '',
    full_name: '',
    lrn_number: '',
    grade_level: '',
    section: '',
    guardian_name: '',
    address: '',
    contact_number: '',
  })
  const [isSaving, setIsSaving] = useState(false)
  const [errors, setErrors] = useState({})

  useEffect(() => {
    if (student) {
      setFormData({
        id_number: student.id_number || '',
        full_name: student.full_name || '',
        lrn_number: student.lrn_number || '',
        grade_level: student.grade_level || '',
        section: student.section || '',
        guardian_name: student.guardian_name || '',
        address: student.address || '',
        contact_number: student.contact_number || '',
      })
      setErrors({})
    }
  }, [student])

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }))
    }
  }

  const validate = () => {
    const newErrors = {}
    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required'
    }
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async () => {
    if (!validate()) return

    setIsSaving(true)
    try {
      await onSave(formData)
    } finally {
      setIsSaving(false)
    }
  }

  const footer = (
    <div className="flex justify-end gap-3">
      <Button variant="secondary" onClick={onClose} disabled={isSaving}>
        Cancel
      </Button>
      <Button
        variant="success"
        icon={FloppyDisk}
        loading={isSaving}
        onClick={handleSubmit}
      >
        Save & Regenerate
      </Button>
    </div>
  )

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Edit Student Information"
      icon={PencilRuler}
      size="md"
      footer={footer}
    >
      <div className="space-y-5">
        <Input
          label="Full Name"
          value={formData.full_name}
          onChange={(e) => handleChange('full_name', e.target.value)}
          error={errors.full_name}
          required
        />

        <Input
          label="ID Number"
          value={formData.id_number}
          disabled
          hint="ID number cannot be changed"
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Grade Level"
            value={formData.grade_level}
            onChange={(e) => handleChange('grade_level', e.target.value)}
          />
          <Input
            label="Section"
            value={formData.section}
            onChange={(e) => handleChange('section', e.target.value)}
          />
        </div>

        <Input
          label="LRN Number"
          value={formData.lrn_number}
          onChange={(e) => handleChange('lrn_number', e.target.value)}
        />

        <Input
          label="Guardian Name"
          value={formData.guardian_name}
          onChange={(e) => handleChange('guardian_name', e.target.value)}
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Address"
            value={formData.address}
            onChange={(e) => handleChange('address', e.target.value)}
          />
          <Input
            label="Contact Number"
            value={formData.contact_number}
            onChange={(e) => handleChange('contact_number', e.target.value)}
          />
        </div>
      </div>
    </Modal>
  )
}
