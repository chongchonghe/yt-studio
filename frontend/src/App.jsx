import { useState, useEffect, useCallback } from 'react'

// Collapsible Section Component
function Section({ title, defaultOpen = true, children }) {
  const [isOpen, setIsOpen] = useState(defaultOpen)
  
  return (
    <div className="section">
      <div className="section-header" onClick={() => setIsOpen(!isOpen)}>
        <span className="section-title">{title}</span>
        <span className={`section-toggle ${isOpen ? 'open' : ''}`}>▼</span>
      </div>
      {isOpen && <div className="section-content">{children}</div>}
    </div>
  )
}

// Format field for display
function formatField(fieldArray) {
  if (!Array.isArray(fieldArray) || fieldArray.length < 2) return ''
  const [namespace, name] = fieldArray
  return namespace === 'gas' ? name : `${namespace}:${name}`
}

function App() {
  // Server state
  const [serverInfo, setServerInfo] = useState(null)
  const [dataDir, setDataDir] = useState('')
  
  // Dataset state
  const [datasets, setDatasets] = useState([])
  const [currentDataset, setCurrentDataset] = useState('')
  const [datasetInfo, setDatasetInfo] = useState(null)
  const [fields, setFields] = useState([])
  
  // Playback state
  const [isPlaying, setIsPlaying] = useState(false)
  const [fps, setFps] = useState(1)
  
  // Plot settings
  const [plotType, setPlotType] = useState('slc')
  const [axis, setAxis] = useState('z')
  const [field, setField] = useState('')
  const [weightField, setWeightField] = useState('None')
  
  // Color settings
  const [cmap, setCmap] = useState('viridis')
  const [logScale, setLogScale] = useState(true)
  const [vmin, setVmin] = useState('')
  const [vmax, setVmax] = useState('')
  
  // Display settings
  const [showColorbar, setShowColorbar] = useState(false)
  const [showScaleBar, setShowScaleBar] = useState(false)
  const [showGrids, setShowGrids] = useState(false)
  const [showTimestamp, setShowTimestamp] = useState(false)
  
  // Width/zoom
  const [widthValue, setWidthValue] = useState('')
  const [widthUnit, setWidthUnit] = useState('')
  
  // Viewer state
  const [imageUrl, setImageUrl] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)
  
  // Volume rendering
  const [cameraTheta, setCameraTheta] = useState(45)
  const [cameraPhi, setCameraPhi] = useState(45)
  const [preview, setPreview] = useState(true)

  // Particles
  const [particleTypes, setParticleTypes] = useState([])
  const [selectedParticles, setSelectedParticles] = useState([])
  const [particleSize, setParticleSize] = useState(10)
  const [particleColor, setParticleColor] = useState('red')

  // Fetch server info and particle types on mount
  useEffect(() => {
    fetch('/api/server_info')
      .then(res => res.json())
      .then(setServerInfo)
      .catch(console.error)
    
    fetch('/api/particle_types')
      .then(res => res.json())
      .then(data => {
        setParticleTypes(data.particle_types || [])
        setParticleSize(data.default_particle_size || 10)
      })
      .catch(console.error)
  }, [])

  // Fetch datasets when server info changes
  useEffect(() => {
    fetchDatasets()
  }, [])

  // Load first dataset when datasets change
  useEffect(() => {
    if (datasets.length > 0 && !currentDataset) {
      loadDataset(datasets[0])
    }
  }, [datasets])

  // Animation loop
  useEffect(() => {
    if (!isPlaying || datasets.length === 0) return
    
    const interval = setInterval(() => {
      const idx = datasets.indexOf(currentDataset)
      const nextIdx = (idx + 1) % datasets.length
      loadDataset(datasets[nextIdx])
    }, 1000 / fps)
    
    return () => clearInterval(interval)
  }, [isPlaying, datasets, currentDataset, fps])

  // Fetch image when settings change
  useEffect(() => {
    if (field && currentDataset) {
      fetchImage()
    }
  }, [
    field, axis, plotType, weightField, cmap, logScale, 
    showColorbar, showScaleBar, showGrids, showTimestamp,
    widthValue, widthUnit, cameraTheta, cameraPhi, preview,
    selectedParticles, particleSize, particleColor,
    refreshKey
  ])

  const fetchDatasets = async () => {
    try {
      const res = await fetch('/api/datasets')
      const data = await res.json()
      setDatasets(data.datasets || [])
    } catch (err) {
      console.error('Failed to fetch datasets:', err)
    }
  }

  const loadDataset = async (name) => {
    if (!name) return
    
    try {
      setCurrentDataset(name)
      const res = await fetch(`/api/load_dataset?filename=${name}`, { method: 'POST' })
      const data = await res.json()
      setDatasetInfo(data)
      
      // Fetch fields
      const fieldsRes = await fetch('/api/fields')
      const fieldsData = await fieldsRes.json()
      setFields(fieldsData.fields || [])
      
      // Set default field if not set
      if (fieldsData.fields?.length > 0) {
        const defaultField = fieldsData.fields.find(f => f[1] === 'density') || fieldsData.fields[0]
        if (defaultField && !field) {
          setField(`${defaultField[0]}:${defaultField[1]}`)
        }
      }
      
      setRefreshKey(k => k + 1)
    } catch (err) {
      console.error('Failed to load dataset:', err)
      setError('Failed to load dataset')
    }
  }

  const fetchImage = useCallback(async () => {
    if (!field) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      const params = new URLSearchParams({
        axis,
        field,
        kind: plotType,
        cmap,
        log_scale: logScale,
        show_colorbar: showColorbar,
        show_scale_bar: showScaleBar,
        grids: showGrids,
        timestamp: showTimestamp,
        dpi: 150,
        preview: preview,
        refreshTrigger: refreshKey
      })
      
      if (weightField && weightField !== 'None') params.set('weight_field', weightField)
      if (vmin) params.set('vmin', vmin)
      if (vmax) params.set('vmax', vmax)
      if (widthValue) params.set('width_value', widthValue)
      if (widthUnit) params.set('width_unit', widthUnit)
      if (selectedParticles.length > 0) {
        params.set('particles', selectedParticles.join(','))
        params.set('particle_size', particleSize)
        params.set('particle_color', particleColor)
      }
      if (plotType === 'vol') {
        params.set('camera_theta', cameraTheta)
        params.set('camera_phi', cameraPhi)
      }
      
      const res = await fetch(`/api/slice?${params}`)
      if (!res.ok) throw new Error('Failed to fetch image')
      
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      setImageUrl(url)
    } catch (err) {
      console.error('Failed to fetch image:', err)
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }, [field, axis, plotType, weightField, cmap, logScale, vmin, vmax, 
      showColorbar, showScaleBar, showGrids, showTimestamp, 
      widthValue, widthUnit, cameraTheta, cameraPhi, preview,
      selectedParticles, particleSize, particleColor, refreshKey])

  const handleSetDataDir = async () => {
    if (!dataDir.trim()) return
    
    try {
      const res = await fetch('/api/set_data_pattern', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pattern: dataDir })
      })
      
      if (res.ok) {
        const data = await res.json()
        console.log(`Found ${data.num_datasets} datasets`)
        fetchDatasets()
      } else {
        const err = await res.json()
        setError(err.detail || 'No datasets found matching pattern')
      }
    } catch (err) {
      setError('Failed to load datasets')
    }
  }

  const handleRefresh = () => {
    setRefreshKey(k => k + 1)
  }

  const handleExport = async () => {
    if (!field) return
    
    try {
      const params = new URLSearchParams({
        axis,
        field,
        kind: plotType,
        cmap,
        log_scale: logScale,
        show_colorbar: showColorbar,
        show_scale_bar: showScaleBar,
        grids: showGrids,
        timestamp: showTimestamp,
        dpi: 300
      })
      
      if (vmin) params.set('vmin', vmin)
      if (vmax) params.set('vmax', vmax)
      if (selectedParticles.length > 0) {
        params.set('particles', selectedParticles.join(','))
        params.set('particle_size', particleSize)
        params.set('particle_color', particleColor)
      }
      
      const res = await fetch(`/api/export/current_frame?${params}`)
      if (!res.ok) throw new Error('Export failed')
      
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${currentDataset}_${field.replace(':', '_')}_${axis}.png`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError('Export failed')
    }
  }

  return (
    <div className="app">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <div className="logo-icon">Q</div>
            <span>QUOKKA Viz</span>
          </div>
          {serverInfo && (
            <div className="server-info">
              {serverInfo.hostname} • {currentDataset || 'No dataset'}
            </div>
          )}
        </div>

        <div className="sidebar-content">
          {/* Data Pattern */}
          <Section title="Data Pattern" defaultOpen={false}>
            <div className="control-row">
              <input
                type="text"
                value={dataDir}
                onChange={e => setDataDir(e.target.value)}
                placeholder="~/data/plt* or /path/to/data"
                onKeyDown={e => e.key === 'Enter' && handleSetDataDir()}
              />
            </div>
            <button className="full-width secondary" onClick={handleSetDataDir}>
              Load Datasets
            </button>
          </Section>

          {/* Plot Type */}
          <Section title="Plot Type">
            <div className="btn-group">
              {['slc', 'prj', 'vol'].map(type => (
                <button
                  key={type}
                  className={plotType === type ? 'active' : ''}
                  onClick={() => setPlotType(type)}
                >
                  {type === 'slc' ? 'Slice' : type === 'prj' ? 'Project' : '3D'}
                </button>
              ))}
            </div>
            
            {plotType !== 'vol' && (
              <div className="control-row" style={{ marginTop: '0.5rem' }}>
                <span className="control-label">Axis</span>
                <div className="btn-group control-input">
                  {['x', 'y', 'z'].map(a => (
                    <button
                      key={a}
                      className={axis === a ? 'active' : ''}
                      onClick={() => setAxis(a)}
                    >
                      {a.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            {plotType === 'prj' && (
              <div className="control-row">
                <span className="control-label">Weight</span>
                <select 
                  className="control-input"
                  value={weightField} 
                  onChange={e => setWeightField(e.target.value)}
                >
                  <option value="None">None</option>
                  <option value="density">Density</option>
                  <option value="cell_volume">Cell Volume</option>
                </select>
              </div>
            )}
            
            {plotType === 'vol' && (
              <>
                <div className="control-row" style={{ marginTop: '0.5rem' }}>
                  <span className="control-label">Theta</span>
                  <input
                    type="number"
                    className="control-input"
                    value={cameraTheta}
                    onChange={e => setCameraTheta(Number(e.target.value))}
                    min="0"
                    max="180"
                  />
                </div>
                <div className="control-row">
                  <span className="control-label">Phi</span>
                  <input
                    type="number"
                    className="control-input"
                    value={cameraPhi}
                    onChange={e => setCameraPhi(Number(e.target.value))}
                    min="0"
                    max="360"
                  />
                </div>
                <label className="checkbox-row">
                  <input
                    type="checkbox"
                    checked={preview}
                    onChange={e => setPreview(e.target.checked)}
                  />
                  <span>Preview mode (faster)</span>
                </label>
              </>
            )}
          </Section>

          {/* Field Selection */}
          <Section title="Field">
            <select 
              value={field} 
              onChange={e => setField(e.target.value)}
              style={{ marginBottom: '0.5rem' }}
            >
              {fields.map(f => {
                const value = `${f[0]}:${f[1]}`
                return (
                  <option key={value} value={value}>
                    {formatField(f)}
                  </option>
                )
              })}
            </select>
            
            <div className="control-row">
              <span className="control-label">Colormap</span>
              <select 
                className="control-input"
                value={cmap} 
                onChange={e => setCmap(e.target.value)}
              >
                {['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'hot', 'jet', 'seismic', 'RdBu'].map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            
            <div className="control-row">
              <span className="control-label">Min</span>
              <input
                type="text"
                className="control-input"
                value={vmin}
                onChange={e => setVmin(e.target.value)}
                placeholder="Auto"
              />
            </div>
            
            <div className="control-row">
              <span className="control-label">Max</span>
              <input
                type="text"
                className="control-input"
                value={vmax}
                onChange={e => setVmax(e.target.value)}
                placeholder="Auto"
              />
            </div>
            
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={logScale}
                onChange={e => setLogScale(e.target.checked)}
              />
              <span>Log scale</span>
            </label>
          </Section>

          {/* Display Options */}
          <Section title="Display" defaultOpen={false}>
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={showColorbar}
                onChange={e => setShowColorbar(e.target.checked)}
              />
              <span>Show colorbar</span>
            </label>
            
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={showScaleBar}
                onChange={e => setShowScaleBar(e.target.checked)}
              />
              <span>Show scale bar</span>
            </label>
            
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={showGrids}
                onChange={e => setShowGrids(e.target.checked)}
              />
              <span>Show AMR grids</span>
            </label>
            
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={showTimestamp}
                onChange={e => setShowTimestamp(e.target.checked)}
              />
              <span>Show timestamp</span>
            </label>
            
            <div className="control-row" style={{ marginTop: '0.5rem' }}>
              <span className="control-label">Width</span>
              <input
                type="text"
                className="control-input"
                value={widthValue}
                onChange={e => setWidthValue(e.target.value)}
                placeholder="Full"
                style={{ flex: 1 }}
              />
              <input
                type="text"
                value={widthUnit}
                onChange={e => setWidthUnit(e.target.value)}
                placeholder="unit"
                style={{ width: '60px' }}
              />
            </div>
          </Section>

          {/* Particles */}
          <Section title={`Particles${selectedParticles.length > 0 ? ` (${selectedParticles.length})` : ''}`} defaultOpen={false}>
            {particleTypes.length > 0 ? (
              <>
                <div style={{ marginBottom: '0.75rem' }}>
                  {particleTypes.map(ptype => (
                    <label key={ptype} className="checkbox-row">
                      <input
                        type="checkbox"
                        checked={selectedParticles.includes(ptype)}
                        onChange={e => {
                          if (e.target.checked) {
                            setSelectedParticles([...selectedParticles, ptype])
                          } else {
                            setSelectedParticles(selectedParticles.filter(p => p !== ptype))
                          }
                        }}
                      />
                      <span>{ptype.replace('_particles', '')}</span>
                    </label>
                  ))}
                </div>
                
                {selectedParticles.length > 0 && (
                  <>
                    <div className="control-row">
                      <span className="control-label">Size</span>
                      <input
                        type="number"
                        className="control-input"
                        value={particleSize}
                        onChange={e => setParticleSize(Number(e.target.value))}
                        min="1"
                        max="50"
                      />
                    </div>
                    
                    <div className="control-row">
                      <span className="control-label">Color</span>
                      <select
                        className="control-input"
                        value={particleColor}
                        onChange={e => setParticleColor(e.target.value)}
                      >
                        {['red', 'white', 'black', 'yellow', 'cyan', 'magenta', 'lime', 'orange'].map(c => (
                          <option key={c} value={c}>{c}</option>
                        ))}
                      </select>
                    </div>
                  </>
                )}
              </>
            ) : (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontStyle: 'italic' }}>
                No particle types available
              </div>
            )}
          </Section>

          {/* Actions */}
          <Section title="Actions">
            <button className="full-width" onClick={handleRefresh}>
              Refresh
            </button>
            <button 
              className="full-width secondary" 
              onClick={handleExport}
              style={{ marginTop: '0.5rem' }}
            >
              Export PNG (300 DPI)
            </button>
          </Section>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Viewer */}
        <div className="viewer">
          {isLoading && (
            <div className="loading-overlay">
              <div className="loading-spinner" />
            </div>
          )}
          
          {error && <div className="error-toast">{error}</div>}
          
          {imageUrl ? (
            <img src={imageUrl} alt="Plot" />
          ) : (
            <div className="viewer-placeholder">
              <div className="viewer-placeholder-icon">◇</div>
              <div>Load a dataset to visualize</div>
            </div>
          )}
        </div>

        {/* Timeline */}
        {datasets.length > 0 && (
          <div className="timeline">
            <div className="timeline-controls">
              <div className="timeline-playback">
                <button 
                  className="play-btn"
                  onClick={() => setIsPlaying(!isPlaying)}
                >
                  {isPlaying ? '⏸' : '▶'}
                </button>
              </div>
              
              <div className="timeline-dataset">
                <select 
                  value={currentDataset} 
                  onChange={e => loadDataset(e.target.value)}
                >
                  {datasets.map(d => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
              
              <div className="btn-group" style={{ width: 'auto' }}>
                {[0.5, 1, 2, 5].map(f => (
                  <button
                    key={f}
                    className={fps === f ? 'active' : ''}
                    onClick={() => setFps(f)}
                    style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                  >
                    {f}x
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
