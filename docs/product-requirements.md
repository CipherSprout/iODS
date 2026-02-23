# ODS Product Requirements Baseline

## 1) Spectacle Frame Selection

### Objective
Help patients choose frames that fit both aesthetics and ergonomics.

### Required capabilities
- Virtual try-on with live camera preview and frame overlay.
- Face-shape-aware recommendations (e.g., round, oval, square, heart).
- Filtering by material, color, brand, size, and price.
- Real-time frame inventory visibility by location.

### Core data points
- Patient style preferences.
- Facial feature profile.
- Frame dimensions and stock levels.

## 2) Ophthalmic Lens Selection

### Objective
Enable accurate, personalized lens choices from prescription and patient context.

### Required capabilities
- Input and validation of prescription values (sphere, cylinder, axis, add, prism).
- Lens material recommendations by use case.
- Coating/package recommendations (AR, blue-filter, photochromic, etc.).
- Lifestyle questionnaire integration (digital use, driving, sports, occupational needs).

### Core data points
- Prescription details.
- Wear context/lifestyle answers.
- Lens portfolio catalog.

## 3) Facial Measurement

### Objective
Capture precise fitting measurements to optimize visual performance and comfort.

### Required capabilities
- Measurement capture for PD (mono/binocular), segment height, fitting cross, and wrap/tilt context.
- Manual entry mode with calibration checks.
- Measurement quality checks and outlier warnings.
- Historical measurement tracking per patient.

### Core data points
- Measurement values and capture timestamps.
- Device/source metadata.
- Validation status.

## 4) Lens Surfacing and Design

### Objective
Support manufacturing calculations for custom lens generation.

### Required capabilities
- Lens geometry calculations from prescription and frame parameters.
- Thickness and curvature computation.
- Rule checks for minimum thickness and decentration constraints.
- Export-ready design packet for lab systems.

### Core data points
- Prescription inputs.
- Frame and fit parameters.
- Lens material/index characteristics.

## 5) Lens Ordering

### Objective
Digitize ordering workflows between optical practices and lens suppliers.

### Required capabilities
- Guided order creation with prescription, material, and coating selections.
- Electronic order submission to manufacturer/lab.
- Order status tracking (submitted, in production, shipped, delivered).
- Error handling for incomplete/invalid orders.

### Core data points
- Order line items.
- Fulfillment statuses and timestamps.
- Supplier acknowledgments.

## 6) Optical Products Marketing

### Objective
Help optical businesses promote services and drive repeat engagement.

### Required capabilities
- Customer segmentation and campaign targeting.
- Promotion scheduling and offer management.
- Multi-channel communication tracking.
- Basic analytics for campaign performance.

### Core data points
- Customer communication preferences.
- Campaign activity and response rates.
- Promotion metadata.

## Cross-cutting non-functional requirements
- Security and privacy controls for patient-sensitive data.
- Role-based access for opticians, sales staff, and administrators.
- Audit trails for clinical and ordering actions.
- Interoperability with lab/manufacturer systems.
- High availability for in-store workflows.
