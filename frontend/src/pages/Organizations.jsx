import { useState } from 'react'
import { Building2, Plus, Pencil, Trash2, FolderOpen, Upload } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useApi } from '../hooks/useApi'
import {
  getOrganizations, createOrganization,
  updateOrganization, deleteOrganization,
} from '../api/organizations'
import Button from '../components/ui/Button'
import Modal from '../components/ui/Modal'
import Input from '../components/ui/Input'
import EmptyState from '../components/ui/EmptyState'
import ErrorState from '../components/ui/ErrorState'

function OrgForm({ initial = {}, onSubmit, loading, serverError }) {
  const [name, setName]   = useState(initial.name ?? '')
  const [desc, setDesc]   = useState(initial.description ?? '')
  const [error, setError] = useState('')

  const handle = async (e) => {
    e.preventDefault()
    setError('')
    if (name.trim().length < 3) { setError('Name must be at least 3 characters.'); return }
    await onSubmit({ name: name.trim(), description: desc.trim() || null })
  }

  return (
    <form onSubmit={handle} className="flex flex-col gap-4">
      <Input
        label="Name"
        value={name}
        onChange={e => setName(e.target.value)}
        placeholder="Acme Corp"
        error={error || serverError}
      />
      <Input
        label="Description (optional)"
        value={desc}
        onChange={e => setDesc(e.target.value)}
        placeholder="A short description"
      />
      <Button type="submit" disabled={loading} className="w-full justify-center">
        {loading ? 'Saving…' : 'Save'}
      </Button>
    </form>
  )
}

export default function Organizations() {
  const { data: orgs, loading, error, refetch } = useApi(getOrganizations)
  const [modal, setModal]       = useState(null)
  const [saving, setSaving]     = useState(false)
  const [saveError, setSaveError] = useState('')
  const [deleting, setDeleting] = useState(null)

  const handleCreate = async (data) => {
    setSaving(true)
    setSaveError('')
    try {
      await createOrganization(data)
      refetch()
      setModal(null)
    } catch (e) {
      setSaveError(e.message)
    } finally {
      setSaving(false)
    }
  }

  const handleUpdate = async (data) => {
    setSaving(true)
    setSaveError('')
    try {
      await updateOrganization(modal.id, data)
      refetch()
      setModal(null)
    } catch (e) {
      setSaveError(e.message)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this organization? All projects and data will be removed.')) return
    setDeleting(id)
    try { await deleteOrganization(id); refetch() }
    catch (e) { alert(e.message) }
    finally { setDeleting(null) }
  }

  const openCreate = () => { setSaveError(''); setModal('create') }
  const openEdit   = (org) => { setSaveError(''); setModal(org) }

  return (
    <div className="flex flex-col gap-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-semibold text-primary">Organizations</h2>
          <p className="text-xs text-secondary mt-0.5">Manage your multi-tenant organizations</p>
        </div>
        <Button onClick={openCreate}>
          <Plus size={14} /> New Organization
        </Button>
      </div>

      {/* States */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="card h-36 animate-pulse" />
          ))}
        </div>
      ) : error ? (
        <div className="card">
          <ErrorState error={error} onRetry={refetch} />
        </div>
      ) : orgs?.length === 0 ? (
        <EmptyState
          icon={Building2}
          title="No organizations yet"
          description="Create your first organization to start managing cloud costs."
          action={<Button onClick={openCreate}><Plus size={14} /> New Organization</Button>}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {orgs.map(org => (
            <div key={org.id} className="card p-5 flex flex-col gap-4 hover:border-accent/30 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-accent/10 flex items-center justify-center text-accent">
                    <Building2 size={16} />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-primary">{org.name}</p>
                    <p className="text-xs text-secondary mt-0.5">{org.description ?? 'No description'}</p>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => openEdit(org)}
                    className="w-7 h-7 rounded-lg flex items-center justify-center text-secondary hover:bg-border hover:text-primary transition-colors"
                  >
                    <Pencil size={13} />
                  </button>
                  <button
                    onClick={() => handleDelete(org.id)}
                    disabled={deleting === org.id}
                    className="w-7 h-7 rounded-lg flex items-center justify-center text-secondary hover:bg-danger/10 hover:text-danger transition-colors disabled:opacity-40"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>

              {/* Quick links */}
              <div className="flex gap-3 pt-2 border-t border-border">
                <Link
                  to={`/organizations/${org.id}/projects`}
                  className="flex items-center gap-1.5 text-xs text-secondary hover:text-accent transition-colors"
                >
                  <FolderOpen size={12} /> Projects
                </Link>
                <span className="text-muted">·</span>
                <Link
                  to={`/organizations/${org.id}/uploads`}
                  className="flex items-center gap-1.5 text-xs text-secondary hover:text-accent transition-colors"
                >
                  <Upload size={12} /> Uploads
                </Link>
                <span className="text-muted">·</span>
                <Link
                  to={`/organizations/${org.id}/billing`}
                  className="flex items-center gap-1.5 text-xs text-secondary hover:text-accent transition-colors"
                >
                  <Pencil size={12} /> Billing
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create modal */}
      <Modal open={modal === 'create'} onClose={() => setModal(null)} title="New Organization">
        <OrgForm onSubmit={handleCreate} loading={saving} serverError={saveError} />
      </Modal>

      {/* Edit modal */}
      <Modal open={!!modal && modal !== 'create'} onClose={() => setModal(null)} title="Edit Organization">
        {modal && modal !== 'create' && (
          <OrgForm initial={modal} onSubmit={handleUpdate} loading={saving} serverError={saveError} />
        )}
      </Modal>
    </div>
  )
}
