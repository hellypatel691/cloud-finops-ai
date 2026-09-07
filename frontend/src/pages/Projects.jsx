import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { FolderOpen, Plus, Pencil, Trash2, ArrowLeft } from 'lucide-react'
import { useApi } from '../hooks/useApi'
import { getProjects, createProject, updateProject, deleteProject } from '../api/projects'
import { getOrganization } from '../api/organizations'
import Button from '../components/ui/Button'
import Modal from '../components/ui/Modal'
import Input from '../components/ui/Input'
import EmptyState from '../components/ui/EmptyState'
import ErrorState from '../components/ui/ErrorState'

function ProjectForm({ initial = {}, onSubmit, loading, serverError }) {
  const [name, setName]   = useState(initial.name ?? '')
  const [desc, setDesc]   = useState(initial.description ?? '')
  const [error, setError] = useState('')

  const handle = async (e) => {
    e.preventDefault()
    if (name.trim().length < 3) { setError('Name must be at least 3 characters.'); return }
    await onSubmit({ name: name.trim(), description: desc.trim() || null })
  }

  return (
    <form onSubmit={handle} className="flex flex-col gap-4">
      <Input label="Name" value={name} onChange={e => setName(e.target.value)} placeholder="Project Alpha" error={error || serverError} />
      <Input label="Description (optional)" value={desc} onChange={e => setDesc(e.target.value)} placeholder="Brief description" />
      <Button type="submit" disabled={loading} className="w-full justify-center">
        {loading ? 'Saving…' : 'Save'}
      </Button>
    </form>
  )
}

export default function Projects() {
  const { orgId } = useParams()
  const { data: org }      = useApi(() => getOrganization(orgId), [orgId])
  const { data: projects, loading, error, refetch } = useApi(() => getProjects(orgId), [orgId])
  const [modal, setModal]     = useState(null)
  const [saving, setSaving]   = useState(false)
  const [saveError, setSaveError] = useState('')

  const handleCreate = async (data) => {
    setSaving(true); setSaveError('')
    try { await createProject(orgId, data); refetch(); setModal(null) }
    catch (e) { setSaveError(e.message) }
    finally { setSaving(false) }
  }

  const handleUpdate = async (data) => {
    setSaving(true); setSaveError('')
    try { await updateProject(orgId, modal.id, data); refetch(); setModal(null) }
    catch (e) { setSaveError(e.message) }
    finally { setSaving(false) }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this project?')) return
    try { await deleteProject(orgId, id); refetch() }
    catch (e) { alert(e.message) }
  }

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link to="/organizations" className="w-8 h-8 rounded-xl bg-card border border-border flex items-center justify-center text-secondary hover:text-primary transition-colors">
            <ArrowLeft size={14} />
          </Link>
          <div>
            <h2 className="text-base font-semibold text-primary">{org?.name ?? 'Organization'} — Projects</h2>
            <p className="text-xs text-secondary mt-0.5">Manage projects within this organization</p>
          </div>
        </div>
        <Button onClick={() => { setSaveError(''); setModal('create') }}><Plus size={14} /> New Project</Button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 3 }).map((_, i) => <div key={i} className="card h-28 animate-pulse" />)}
        </div>
      ) : error ? (
        <div className="card"><ErrorState error={error} onRetry={refetch} /></div>
      ) : projects?.length === 0 ? (
        <EmptyState
          icon={FolderOpen}
          title="No projects yet"
          description="Create a project to start grouping your billing data."
          action={<Button onClick={() => setModal('create')}><Plus size={14} /> New Project</Button>}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map(p => (
            <div key={p.id} className="card p-5 flex flex-col gap-3 hover:border-accent/30 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-accent/10 flex items-center justify-center text-accent">
                    <FolderOpen size={16} />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-primary">{p.name}</p>
                    <p className="text-xs text-secondary">{p.description ?? 'No description'}</p>
                  </div>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => { setSaveError(''); setModal(p) }} className="w-7 h-7 rounded-lg flex items-center justify-center text-secondary hover:bg-border hover:text-primary transition-colors">
                    <Pencil size={13} />
                  </button>
                  <button onClick={() => handleDelete(p.id)} className="w-7 h-7 rounded-lg flex items-center justify-center text-secondary hover:bg-danger/10 hover:text-danger transition-colors">
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modal === 'create'} onClose={() => setModal(null)} title="New Project">
        <ProjectForm onSubmit={handleCreate} loading={saving} serverError={saveError} />
      </Modal>
      <Modal open={!!modal && modal !== 'create'} onClose={() => setModal(null)} title="Edit Project">
        {modal && modal !== 'create' && <ProjectForm initial={modal} onSubmit={handleUpdate} loading={saving} serverError={saveError} />}
      </Modal>
    </div>
  )
}
