"""Public worked example: Elucidating Flow Matching ODE Dynamics via Data Geometry and Denoisers.

The main paper is partitioned bottom-up. The principal theorem proofs and all experiment
sections are dissected beyond that boundary; the remainder of the appendix stays visible as
undissected source. Run with the repository skill's scripts on PYTHONPATH, or set
PAPER_DISSECT_SCRIPTS to that directory.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.environ.get(
    "PAPER_DISSECT_SCRIPTS",
    os.path.abspath(os.path.join(HERE, "..", "..", "skills", "paper-dissect", "scripts")),
)
sys.path.insert(0, SCRIPTS)
from dissect_lib import Dissection

skeleton, out = sys.argv[1], sys.argv[2]
D = Dissection(
    skeleton,
    arxiv="2412.18730",
    title="Elucidating Flow Matching ODE Dynamics via Data Geometry and Denoisers",
    dissected_through="s0353",
    source_id="arxiv-2412.18730",
)


# ---- Abstract and introduction -------------------------------------------------
D.discard("declaration", "s0001")
D.statement("bg_fm", "Flow matching is an efficient ODE generative framework", "Flow matching extends ODE samplers into a general framework with learned vector fields and fewer sampling steps.", warrant="cited", function="context", spans=D.sp(("s0012", "s0018"), ("s0022", "s0023")), echoes=D.sp("s0002"))
D.statement("problem_geometry", "Per-sample FM geometry is poorly understood", "Theory had not adequately explained how individual flow-matching trajectories interact with clusters, manifolds, and other data geometry.", warrant="interpreted", function="problem", spans=D.sp("s0003"))
D.statement("motivation_rigour", "Trajectory theory matters for stability and one-step distillation", "Terminal convergence and geometric trajectory understanding matter for stable sampling, consistency-style distillation, steering, and latent-space design.", warrant="interpreted", function="motivation", spans=D.sp(("s0026", "s0027")), echoes=D.sp("s0004"))
D.target("q_geometry", "How does data geometry guide an individual FM trajectory?", "Explain how coarse and fine data geometry controls the evolution of each sample path.", subtype="research_question", spans=D.sp("s0024"))
D.target("q_terminal", "Do FM trajectories converge at terminal time on singular supports?", "Determine whether each trajectory converges as t approaches 1, including when the target is supported on a subspace or manifold.", subtype="research_question", spans=D.sp("s0025"))
D.construct("m_denoiser_lens", "Analyze the ODE through its denoiser", "Use the conditional mean of clean data given the noisy state as the only data-dependent component of the FM vector field.", subtype="method", function="approach", spans=D.sp("s0029"), echoes=D.sp("s0005"), story=True)
D.statement("c_denoiser_geometry", "The denoiser turns data geometry into attraction and absorption", "The denoiser guides an FM trajectory toward geometric sets and can keep it inside their neighborhoods.", warrant="interpreted", function="theory_answer", spans=D.sp("s0030"), echoes=D.sp("s0006"))
D.statement("c_three_stages", "FM trajectories exhibit mean, cluster, and terminal stages", "The trajectory first aligns with the data mean, then responds to local clusters, and finally converges toward the fine-scale support.", warrant="interpreted", function="contribution", spans=D.sp(("s0031", "s0034")), echoes=D.sp("s0007"))
D.statement("c_terminal_answer", "Under regular support geometry, the terminal flow map exists", "Under the paper's finite-moment, positive-reach, and local-mass assumptions, almost every FM path has a terminal limit that pushes the prior to the data law.", warrant="interpreted", function="theory_answer", spans=D.sp(("s0263", "s0264")), echoes=D.sp("s0008"))
D.statement("c_terminal_consequences", "Terminal analysis yields equivariance and a memorization mechanism", "Once the terminal map is controlled, the paper derives similarity equivariance and explains why an asymptotically empirical denoiser reproduces training atoms.", warrant="interpreted", function="contribution", spans=D.sp("s0009"))
D.statement("c_practical", "Geometry suggests where sampling and representation effort should go", "The theory suggests reallocating solver effort toward the evolving middle stage and designing latent geometry or terminal regularization deliberately.", warrant="interpreted", function="interpretation", spans=D.sp("s0010"))
D.discard("illustration", ("s0019", "s0021"))
D.discard("signpost", "s0028")
D.statement("obs_three_stage_figure", "A synthetic path visibly passes through three stages", "The worked synthetic trajectory moves toward the mean, enters a local cluster, and converges to one data point.", warrant="observed", function="evidence", spans=D.sp(("s1565", "s1567")), echoes=D.sp("s0035"))
D.discard("signpost", "s0036")
D.statement("intro_framework", "Attraction, absorption, and posterior concentration organize the theory", "The paper's roadmap combines preterminal well-posedness, denoiser-based attracting and absorbing results, and posterior concentration to analyze all trajectory stages.", warrant="interpreted", function="contribution", spans=D.sp(("s0037", "s0038")), echoes=D.sp("s0395"))
D.statement("intro_stage_results", "Formal results cover well-posedness, mean attraction, and clusters", "The main results establish preterminal existence and quantify the initial mean and intermediate cluster regimes.", warrant="interpreted", function="contribution", spans=D.sp("s0039"))
D.statement("intro_terminal_result", "Formal terminal convergence includes manifold-supported data", "The terminal theorem covers low-dimensional manifold support under the stated assumptions.", warrant="interpreted", function="contribution", spans=D.sp(("s0040", "s0041")))
D.statement("intro_equivariance", "The terminal map is equivariant under similarities", "Appropriately transformed schedules make the flow map commute with scaling, rotation, and translation.", warrant="interpreted", function="contribution", spans=D.sp("s0042"))
D.statement("intro_memorization", "Near-terminal empirical denoisers expose memorization", "For discrete empirical targets, terminal-time behavior ties learned denoiser optimality to convergence onto training examples.", warrant="interpreted", function="contribution", spans=D.sp("s0043"))
D.discard("pointer", ("s0044", "s0045"))
D.statement("intro_appendix_results", "The appendix analyzes singularities and geometry-dependent rates", "Additional results describe terminal vector-field blow-up and posterior/denoiser convergence rates for general, manifold, and discrete supports.", warrant="interpreted", function="contribution", spans=D.sp("s0046"))


# ---- Background and coordinate system -----------------------------------------
D.construct("d_geometry", "Geometry notation: support, projection, medial axis, reach", "Distance, projection, convex hull, medial axis, reach, Dirac measures, Gaussians, and Wasserstein distance fix the geometric language.", subtype="definition", function="setup", spans=D.sp(("s0048", "s0057")))
D.discard("pointer", "s0058")
D.construct("d_fm_path", "FM probability path and ODE", "A Gaussian conditional path interpolates a standard-normal prior and data distribution; a marginal vector field transports the prior along that path.", subtype="construction", function="setup", spans=D.sp(("s0060", "s0063"), ("s0068", "s0076")), story=True)
D.statement("a_schedule", "Schedules are smooth, usually monotone, with fixed endpoints", "The analysis assumes smooth schedules on [0,1], and the noise-to-signal reparameterization additionally uses strict monotonicity.", warrant="assumed", function="setup", spans=D.sp(("s0064", "s0067")))
D.statement("bg_path_generation", "The conditional FM field generates the marginal path when the ODE exists", "Prior work proves that the conditional-field marginalization generates the prescribed path, conditional on ODE existence.", warrant="cited", function="context", spans=D.sp(("s0077", "s0079")))
D.construct("m_training", "Conditional flow-matching regression", "Train a neural vector field against the analytic conditional velocity by squared error.", subtype="method", function="setup", spans=D.sp(("s0080", "s0081")))
D.discard("signpost", "s0082")
D.construct("d_sigma", "Noise-to-signal coordinate sigma = beta / alpha", "Strictly monotone schedules map time to decreasing noise level; q_sigma is the data law convolved with Gaussian noise.", subtype="representation", function="approach", spans=D.sp(("s0083", "s0091")), story=True)
D.discard("signpost", "s0092")
D.skeleton_env("prop:equivalence_variance_exploding", "r_scaled_path", "Proposition 1 — scaling converts p_t to q_sigma", warrant="proved", function="guarantee")
D.edge_evidence("s0096", "r_scaled_path", "r_sigma_ode")
D.skeleton_env("prop:equivalence_ode", "r_sigma_ode", "Proposition 2 — the scaled path obeys the score ODE", warrant="proved", function="guarantee")
D.statement("c_schedule_free", "The sigma coordinate removes schedule-specific clutter", "Expressing the dynamics in noise-to-signal coordinates yields one schedule-independent analysis.", warrant="interpreted", function="interpretation", spans=D.sp(("s0102", "s0104")))
D.statement("rw_mean_shift", "Prior work links denoisers, mean shift, and projection", "Related analyses connect FM sampling with mean shift and show near-support denoisers approach projection.", warrant="cited", function="context", spans=D.sp(("s0106", "s0107")))
D.statement("c_beyond_prior", "This work targets almost-everywhere convergence and full path stages", "The paper claims broader fixed-point convergence and a three-stage per-trajectory account beyond prior approximate-projection interpretations.", warrant="interpreted", function="comparison", spans=D.sp("s0108"))
D.statement("rw_discrete", "Prior discrete analyses assume convergence or bounded priors", "Earlier discrete-support and cluster analyses leave terminal convergence implicit or rely on bounded prior support.", warrant="cited", function="context", spans=D.sp(("s0109", "s0110")))
D.statement("c_rigorous_path", "The paper supplies a convergence proof and full evolution analysis", "It aims to close the convergence gap and analyze the whole individual trajectory.", warrant="interpreted", function="comparison", spans=D.sp("s0111"))
D.statement("rw_concurrent_mem", "Concurrent work also studies Voronoi-based memorization", "Concurrent memorization analysis uses related discrete geometry and proposes regularization.", warrant="cited", function="context", spans=D.sp(("s0112", "s0114")))


# ---- Denoiser, attraction, and absorption --------------------------------------
D.statement("d_denoiser_role", "The denoiser fully determines the FM vector field", "The posterior conditional mean is the only data-dependent quantity in the analytic FM field.", warrant="derived", function="setup", spans=D.sp(("s0116", "s0117")))
D.construct("d_denoiser", "Denoiser m_t and m_sigma", "The denoiser is the posterior mean under the Gaussian-corrupted observation model; it may be trained directly by denoising regression.", subtype="definition", function="approach", spans=D.sp(("s0119", "s0125"), ("s0130", "s0131")), story=True)
D.statement("c_denoiser_stability", "Denoiser regression can stay bounded when velocity regression blows up", "For each state the denoiser remains bounded even when the terminal-time velocity can diverge, motivating direct denoiser learning.", warrant="interpreted", function="interpretation", spans=D.sp("s0126"))
D.construct("d_denoiser_ode", "Sigma-ODE moves from the state toward the denoiser", "In sigma coordinates, dx/dsigma = -(m_sigma(x)-x)/sigma, so backward integration moves in the denoiser direction.", subtype="representation", function="approach", spans=D.sp(("s0127", "s0129")), story=True)
D.statement("problem_moving_target", "The denoiser target changes along the path", "Although the vector points toward the denoiser, the denoiser itself evolves with state and noise, so trajectory geometry is not immediate.", warrant="interpreted", function="problem", spans=D.sp(("s0133", "s0135")))
D.construct("m_projection_test", "Compare the denoiser with projection onto a closed set", "Use the angle between denoiser direction and nearest-point projection to certify attraction and absorption.", subtype="method", function="approach", spans=D.sp(("s0136", "s0139")), story=True)
D.discard("signpost", "s0140")
D.construct("d_acute_angle", "Acute-angle attraction condition", "Distance to a closed set falls when the denoiser direction has positive inner product with the projection direction.", subtype="definition", function="setup", spans=D.sp(("s0141", "s0144")))
D.discard("illustration", "s0145")
D.statement("c_angle_attracts", "A quantitative acute-angle bound forces attraction", "Controlling the projection-angle error yields decay of distance to the set.", warrant="interpreted", function="theory_answer", spans=D.sp("s0146"))
D.skeleton_env("thm:attracting_toward_set_meta_informal", "r_attract_informal", "Theorem 3.1 — quantitative angle control attracts trajectories", warrant="proved", function="guarantee")
D.discard("pointer", "s0150")
D.statement("a_medial_axis", "Attraction requires avoiding the medial axis", "Projection must stay single-valued; convex sets satisfy this automatically, while absorption can keep nonconvex cases away from singularities.", warrant="assumed", function="setup", spans=D.sp(("s0151", "s0152")))
D.discard("signpost", "s0153")
D.construct("d_absorbing", "Absorbing set", "A set is absorbing over a noise interval when every path starting inside remains inside throughout the interval.", subtype="definition", function="setup", spans=D.sp(("s0154", "s0155")))
D.skeleton_env("thm:absorbing_by_neighborhoods_meta", "r_absorb", "Theorem 3.2 — acute-angle boundaries make neighborhoods absorbing", warrant="proved", function="guarantee")
D.skeleton_env("rem:absorbing_property", "r_absorb_local", "Remark — absorption needs only regional denoiser control", warrant="derived", function="interpretation")
D.discard("signpost", "s0164")
D.statement("c_convex_hull", "Every FM path is pulled toward the data convex hull", "Because posterior means lie in the convex hull of the support, that hull is attracting and absorbing.", warrant="interpreted", function="theory_answer", spans=D.sp(("s0165", "s0168")))
D.skeleton_env("prop:initial_stage_convex_hull", "r_convex_hull", "Proposition 3.3 — convex-hull distance decays linearly in sigma", warrant="proved", function="guarantee")
D.discard("pointer", ("s0175", "s0176"))
D.statement("problem_terminal_singularity", "Terminal geometry requires avoiding projection singularities", "Near terminal time the analysis must keep trajectories away from the support's medial axis while proving integrable attraction.", warrant="interpreted", function="problem", spans=D.sp("s0177"))


# ---- Preterminal stages --------------------------------------------------------
D.statement("c_preterminal_overview", "Preterminal dynamics combine existence, mean attraction, and clusters", "The preterminal story first guarantees trajectories exist, then identifies mean and cluster attraction regimes.", warrant="interpreted", function="contribution", spans=D.sp(("s0179", "s0182")))
D.statement("c_wellposed", "FM ODEs are well posed on every preterminal interval", "A finite second moment suffices for a unique path from every initial point and a continuous flow transporting the prior to p_t for t<1.", warrant="interpreted", function="theory_answer", spans=D.sp("s0184"))
D.skeleton_env("prop:existence of flow maps", "r_preterminal", "Theorem 4.1 — preterminal existence, uniqueness, and pushforward", warrant="proved", function="guarantee")
D.statement("m_wellposed_proof", "Posterior covariance controls local Lipschitzness", "The proof bounds denoiser growth and posterior covariance, then applies continuity-equation flow theory.", warrant="derived", function="setup", spans=D.sp(("s0188", "s0191")))
D.statement("c_mean", "At large noise, trajectories move toward the data mean", "Because the denoiser approaches the data mean at the initial endpoint, a quantitative high-noise interval contracts mean distance.", warrant="interpreted", function="theory_answer", spans=D.sp(("s0193", "s0194")))
D.skeleton_env("prop:initial-stage_mean_geneal", "r_mean", "Proposition 4.2 — a quantitative initial mean-attraction regime", warrant="proved", function="guarantee")
D.statement("l_mean_tradeoff", "The mean-stage interval and rate trade off through zeta", "Increasing zeta extends the certified interval but weakens the contraction exponent.", warrant="bounded", function="boundary", spans=D.sp(("s0202", "s0203")))
D.statement("c_cluster", "At intermediate noise, coarse clusters capture trajectories", "For a separated local cluster, nearby trajectories are absorbed near its convex hull and converge toward that hull.", warrant="interpreted", function="theory_answer", spans=D.sp(("s0205", "s0207")))
D.statement("a_local_cluster", "Local-cluster assumption: bounded and separated beyond twice its diameter", "A positive-mass cluster S is bounded and every support point outside it stays more than twice its diameter from conv(S).", warrant="assumed", function="setup", spans=D.sp(("s0208", "s0210")))
D.skeleton_env("prop:local_cluster_denoiser_convergence_sigma", "r_cluster_denoiser", "Proposition 4.3 — the denoiser concentrates near a local cluster", warrant="proved", function="guarantee")
D.skeleton_env("prop:local_cluster_convergence_sigma", "r_cluster", "Proposition 4.4 — local-cluster neighborhoods absorb and attract", warrant="proved", function="guarantee")
D.statement("c_cluster_weight", "Heavier clusters attract over a wider noise range", "The certified threshold becomes unbounded when the cluster's mass makes its attraction sufficiently strong.", warrant="interpreted", function="interpretation", spans=D.sp(("s0218", "s0219")))
D.statement("l_cluster_scope", "Exact separation is sufficient, not empirically necessary", "Real data need not satisfy the local-cluster assumption; experiments suggest attraction to overlapping dense regions, and a smoothed-cluster corollary gives partial theory.", warrant="bounded", function="boundary", spans=D.sp(("s0220", "s0224")))
D.statement("c_cluster_implication", "Cluster absorption suggests feature locking and latent-space design", "The authors interpret absorption as a locking mechanism that may support feature separation, mode coverage, and geometry-aware latent design.", warrant="interpreted", function="interpretation", spans=D.sp(("s0225", "s0227")))
D.statement("c_to_terminal", "Fine-scale support geometry takes over as noise vanishes", "Near zero noise, attraction shifts from coarse clusters toward nearest support points or manifold geometry.", warrant="interpreted", function="interpretation", spans=D.sp(("s0228", "s0229")))


# ---- Terminal convergence and consequences ------------------------------------
D.statement("problem_distribution_not_path", "Distributional convergence does not imply pathwise convergence", "Even if transported distributions approach the data law, individual paths could wind indefinitely; a terminal flow map requires pointwise limits.", warrant="interpreted", function="problem", spans=D.sp(("s0231", "s0233")))
D.target("q_terminal_map", "When does the terminal flow map exist and transport to p?", "Find conditions ensuring almost-everywhere path convergence at t=1 and identify its rate.", subtype="design_goal", spans=D.sp(("s0234", "s0235")))
D.statement("problem_singular_integral", "Terminal convergence must cancel the 1/sigma singularity", "The denoiser-state gap must vanish fast enough to make the sigma-ODE integrable.", warrant="interpreted", function="problem", spans=D.sp(("s0237", "s0238")))
D.skeleton_env("thm:denoiser_limit", "r_denoiser_projection", "Theorem 5.1 — the denoiser converges to projection off the medial axis", warrant="proved", function="guarantee")
D.statement("m_posterior_rate", "Posterior concentration supplies a usable denoiser rate", "Geometry-dependent posterior rates strengthen absorption, keep paths off the medial axis, and make their terminal motion integrable.", warrant="derived", function="setup", spans=D.sp(("s0242", "s0246")))
D.discard("signpost", "s0247")
D.skeleton_env("assumption:data_distribution", "a_terminal", "Assumption 5.2 — positive reach and local lower mass", warrant="assumed", function="setup")
D.statement("a_terminal_examples", "Discrete laws and regular manifold densities meet the terminal assumptions", "Discrete targets use k=0; nonvanishing densities on positive-reach compact manifolds use intrinsic dimension k=m.", warrant="derived", function="setup", spans=D.sp(("s0251", "s0254")))
D.discard("signpost", "s0255")
D.skeleton_env("thm:existence of flow maps", "r_terminal", "Theorem 5.3 — an a.e. terminal map exists and pushes prior to data", warrant="proved", function="guarantee")
D.skeleton_env("thm:existence of flow maps different geometries", "r_terminal_rates", "Theorem 5.4 — manifold and discrete terminal rates", warrant="proved", function="guarantee")
D.construct("ex_subspace", "Closed-form subspace example", "A Gaussian target on a linear subspace splits tangential FM dynamics from normal contraction and reaches the terminal point at linear rate.", subtype="construction", function="setup", spans=D.sp(("s0274", "s0286")))
D.statement("q_manifold_rate", "Can the manifold trajectory rate be sharpened to linear?", "The subspace example and distribution-level Wasserstein rate suggest O(sigma), rather than the proved O(sqrt(sigma)), may be possible.", warrant="conjectured", function="future", spans=D.sp(("s0287", "s0288")))
D.skeleton_env("prop: linear convergence probability", "r_distribution_rate", "Proposition 5.5 — q_sigma approaches p at linear Wasserstein rate", warrant="proved", function="guarantee")
D.statement("c_sparse_terminal_steps", "The certified terminal regime suggests fewer late solver steps", "If terminal movement is small, computation may be reallocated away from late time without harming quality.", warrant="interpreted", function="interpretation", spans=D.sp("s0291"))
D.target("q_equivariance", "How does the terminal map transform under similarities?", "Determine whether transforming the data by scale, rotation, and translation commutes with FM sampling.", subtype="research_question", spans=D.sp(("s0292", "s0294")))
D.construct("m_schedule_transform", "Transform the schedules with the data similarity", "For T(x)=gamma(Ox+b), use bar-alpha=s_t alpha/gamma and bar-beta=s_t beta with matched endpoints.", subtype="method", function="approach", spans=D.sp(("s0295", "s0298")), story=True)
D.skeleton_env("thm:similarity_transform", "r_equivariance", "Proposition 5.7 — flow maps are similarity-equivariant", warrant="proved", function="guarantee")
D.skeleton_env("remark:2", "r_affine_subspace", "Remark — affine-subspace sampling reduces to intrinsic coordinates", warrant="derived", function="interpretation")
D.statement("a_empirical_target", "Memorization analysis uses a finite empirical target", "The terminal memorization section assumes a discrete weighted data measure, matching empirical training distributions.", warrant="assumed", function="setup", spans=D.sp(("s0307", "s0309")))
D.construct("d_shrunk_voronoi", "Shrunk Voronoi cells and their absorption threshold", "An epsilon margin selects points unambiguously assigned to one training atom; a mass- and separation-dependent sigma threshold controls when the cell becomes absorbing.", subtype="definition", function="setup", spans=D.sp(("s0310", "s0316")))
D.statement("c_duplicate_risk", "Higher weight or separation makes a training atom attract earlier", "The threshold increases for heavier or more isolated atoms, connecting duplicates and isolated samples with memorization risk.", warrant="interpreted", function="interpretation", spans=D.sp(("s0317", "s0318")))
D.skeleton_env("prop:V_epsilon_i_absorbing_sigma", "r_atom_absorption", "Proposition 5.9 — a shrunk Voronoi cell converges to its atom", warrant="proved", function="guarantee")
D.discard("signpost", "s0323")
D.statement("d_memorization", "Memorization means reproducing training data rather than generalizing", "For an empirical target, the population-optimal denoiser and velocity reproduce the finite training measure.", warrant="derived", function="setup", spans=D.sp(("s0324", "s0325")))
D.statement("c_terminal_training", "The final sampling stage is the critical memorization regime", "For CIFAR-10 the estimated atom-attraction threshold falls in the last quarter of the EDM schedule, motivating less-than-optimal terminal training.", warrant="interpreted", function="interpretation", spans=D.sp(("s0326", "s0328")))
D.construct("d_learned_ode", "ODE driven by a learned denoiser", "Replace the exact posterior mean by a smooth learned denoiser m_theta in the same sigma dynamics.", subtype="model", function="setup", spans=D.sp(("s0329", "s0330")))
D.discard("signpost", "s0331")
D.skeleton_env("prop:memorization_sigma", "r_learned_mem", "Proposition 5.10 — asymptotically optimal denoisers memorize atoms", warrant="proved", function="guarantee")
D.target("q_memorization", "What must change near terminal time for the model to generalize?", "Identify why an empirical optimum memorizes and what a learned denoiser must do differently.", subtype="research_question", spans=D.sp(("s0337", "s0338")))
D.discard("pointer", "s0339")


# ---- Discussion, limits, and impact -------------------------------------------
D.statement("c_discussion", "The geometry view informs solver allocation, latent design, and regularization", "The authors propose sparse effort in calm initial/terminal stages, geometry-aware embeddings, and Jacobian regularization near terminal time.", warrant="interpreted", function="interpretation", spans=D.sp(("s0341", "s0345")))
D.statement("a_independent_coupling", "The path construction assumes independent data and prior noise", "The analysis does not cover dependent endpoint-noise couplings used by rectification or coupling-based FM variants.", warrant="bounded", function="boundary", spans=D.sp("s0346"))
D.target("q_dependent", "Open — extend the theory to dependent couplings", "Analyze rectified or deliberately coupled flow-matching paths where clean data and prior noise are dependent.", subtype="open_question", spans=D.sp(("s0347", "s0348")))
D.discard("declaration", ("s0350", "s0351"))
D.discard("courtesy", "s0353")


# ---- Principal appendix results and proof graphs -------------------------------
D.skeleton_env("thm:attracting_toward_set_meta", "r_attract_formal", "Theorem C.7 — formal attraction inequality", warrant="proved", function="guarantee")
D.proof("pf_attract", parent="r_attract_formal", label="Proof of the attraction theorem", text="Differentiate squared distance in lambda-time and integrate the resulting differential inequality.", spans=D.sp("s0693"))
D.step("pa1", parent="pf_attract", label="1 · Reparameterize by lambda and differentiate distance", text="Use the directional derivative formula for distance to the set.", spans=D.sp(("s0694", "s0699")))
D.step("pa2", parent="pf_attract", label="2 · Quantitative angle control gives exponential decay", text="An integrating factor yields the stated sigma power law.", spans=D.sp(("s0700", "s0706")))
D.step("pa3", parent="pf_attract", label="3 · Vanishing perturbation gives asymptotic attraction", text="Apply the scalar ODE lemma and translate back to sigma.", spans=D.sp(("s0707", "s0715")))
D.proof("pf_absorb", parent="r_absorb", label="Proof of the absorbing-set theorem", text="A first-exit contradiction shows the vector field cannot cross the boundary outward.", spans=D.sp("s0718"))
D.step("pb1", parent="pf_absorb", label="1 · Assume a first boundary exit", text="Switch to lambda-time and choose the first contact with the boundary.", spans=D.sp(("s0719", "s0722")))
D.step("pb2", parent="pf_absorb", label="2 · The boundary derivative points inward", text="The acute-angle condition makes squared distance decrease at first contact.", spans=D.sp(("s0723", "s0728")))
D.step("pb3", parent="pf_absorb", label="3 · Intersecting all absorbing neighborhoods preserves the set", text="Closedness proves the second statement.", spans=D.sp(("s0729", "s0731")))

D.proof("pf_preterminal", parent="r_preterminal", label="Proof of preterminal well-posedness", text="Verify continuity-equation flow hypotheses using posterior covariance, growth, and integrability estimates.", spans=D.sp("s1193"))
D.step("pw1", parent="pf_preterminal", label="1 · State the continuity-equation flow criterion", text="Existence, uniqueness, pushforward, and continuity follow once three analytic bounds hold.", spans=D.sp(("s1194", "s1207")))
D.step("pw2", parent="pf_preterminal", label="2 · Upgrade almost-everywhere flow to every initial point", text="Local uniqueness plus linear growth prevents finite-time escape.", spans=D.sp(("s1208", "s1223")))
D.step("pw3", parent="pf_preterminal", label="3 · Verify the path and velocity are integrable", text="Gaussian conditional velocities and the finite second moment give the required spacetime integral.", spans=D.sp(("s1224", "s1242")))
D.step("pw4", parent="pf_preterminal", label="4 · Posterior covariance gives local Lipschitzness", text="Differentiate the denoiser and bound its conditional covariance on compacts.", spans=D.sp(("s1243", "s1273")))
D.step("pw5", parent="pf_preterminal", label="5 · Bound denoiser and velocity growth linearly", text="Tail decomposition and Markov bounds produce a time-local linear growth estimate.", spans=D.sp(("s1274", "s1311")))
D.step("pw6", parent="pf_preterminal", label="6 · Apply the criterion", text="All hypotheses now hold.", spans=D.sp("s1312"))

D.proof("pf_mean", parent="r_mean", label="Proof of initial mean attraction", text="Control the high-noise posterior, obtain an absorbing mean ball, then invoke the attraction theorem.", spans=D.sp("s1313"))
D.step("pm1", parent="pf_mean", label="1 · High-noise posterior stays close to the data law", text="A likelihood-ratio bound controls total variation and Wasserstein distance.", spans=D.sp(("s1314", "s1335")))
D.step("pm2", parent="pf_mean", label="2 · The denoiser remains inside a smaller mean ball", text="Wasserstein stability of the mean turns posterior closeness into the denoiser estimate.", spans=D.sp(("s1336", "s1351")))
D.step("pm3", parent="pf_mean", label="3 · Absorption propagates the estimate along the trajectory", text="The mean ball is absorbing, so the attraction theorem yields the rate.", spans=D.sp(("s1352", "s1356")))
D.step("pm4", parent="pf_mean", label="4 · Gaussian smoothing is an early-stop reparameterization", text="Combine the bounded-support proof with the smoothing lemma.", spans=D.sp(("s1357", "s1358")))

D.proof("pf_cluster_denoiser", parent="r_cluster_denoiser", label="Proof of cluster posterior concentration", text="Restrict the posterior to the cluster and couple its complement back into the cluster.", spans=D.sp("s1128"))
D.step("pcd1", parent="pf_cluster_denoiser", label="1 · Restrict the posterior to S", text="Its conditional mean lies in conv(S).", spans=D.sp(("s1129", "s1131")))
D.step("pcd2", parent="pf_cluster_denoiser", label="2 · Couple out-of-cluster mass to the restricted posterior", text="Cluster separation creates an exponential likelihood gap.", spans=D.sp(("s1132", "s1142")))
D.step("pcd3", parent="pf_cluster_denoiser", label="3 · Wasserstein control bounds denoiser distance", text="Mean stability gives the proposition.", spans=D.sp(("s1143", "s1144")))
D.proof("pf_cluster", parent="r_cluster", label="Proof of cluster absorption and attraction", text="First certify an invariant convex neighborhood, then integrate the cluster-distance inequality.", spans=D.sp("s1145"))
D.step("pc1", parent="pf_cluster", label="1 · The denoiser maps the boundary inside", text="The posterior concentration bound and sigma threshold imply absorption.", spans=D.sp(("s1146", "s1156")))
D.step("pc2", parent="pf_cluster", label="2 · Differentiate distance to conv(S)", text="Split the denoiser around its cluster-restricted mean.", spans=D.sp(("s1157", "s1165")))
D.step("pc3", parent="pf_cluster", label="3 · Integrate the super-exponentially small forcing", text="The meta-attraction inequality produces convergence and an explicit bound.", spans=D.sp(("s1166", "s1175")))

D.skeleton_env("thm:denoiser_limit_sigma", "r_posterior_projection", "Theorem D.1 — the posterior concentrates at geometric projection", warrant="proved", function="guarantee")
D.proof("pf_projection", parent="r_posterior_projection", label="Proof of posterior concentration", text="Split posterior second moment into a local projection ball and an exponentially suppressed tail.", spans=D.sp("s0847"))
D.step("pp1", parent="pf_projection", label="1 · Geometry turns a ball around x into a projection ball", text="Local feature size supplies nested radii around x and proj(x).", spans=D.sp(("s0848", "s0856")))
D.step("pp2", parent="pf_projection", label="2 · Split the Wasserstein moment", text="The near term is at most epsilon squared.", spans=D.sp(("s0857", "s0860")))
D.step("pp3", parent="pf_projection", label="3 · Suppress the far term exponentially", text="Lower-bound posterior normalization by local support mass.", spans=D.sp(("s0861", "s0865")))
D.step("pp4", parent="pf_projection", label="4 · Send sigma to zero, then epsilon to zero", text="This proves posterior and hence denoiser convergence.", spans=D.sp(("s0866", "s0868")))
D.proof("pf_denoiser_projection", parent="r_denoiser_projection", label="Proof of denoiser-to-projection convergence", text="Wasserstein convergence controls the difference of posterior means.", spans=D.sp(("s0869", "s0874")))

D.proof("pf_terminal", parent="r_terminal", label="Proof of terminal flow-map convergence", text="Combine posterior rates, an absorbing tube, high-probability entry, and a Cauchy estimate for trajectories.", spans=D.sp("s1426"))
D.step("pt1", parent="pf_terminal", label="1 · Move to lambda-time and the blurred law q_lambda", text="The scaled trajectory obeys dz/dlambda=m_lambda(z)-z.", spans=D.sp(("s1427", "s1433")))
D.step("pt2", parent="pf_terminal", label="2 · Make posterior convergence uniform in a bounded tube", text="The local-mass assumption turns the pointwise rate into a regional bound.", spans=D.sp(("s1434", "s1442")))
D.step("pt3", parent="pf_terminal", label="3 · Build an absorbing bounded tube near the support", text="The contraction theorem keeps any entered path in a slightly enlarged tube.", spans=D.sp(("s1443", "s1449")))
D.step("pt4", parent="pf_terminal", label="4 · q_lambda enters that tube with high probability", text="Couple data with vanishing Gaussian noise and control tails.", spans=D.sp(("s1450", "s1463")))
D.step("pt5", parent="pf_terminal", label="5 · Terminal paths are Cauchy with an explicit rate", text="Integrate projection error plus distance-to-support inside the tube.", spans=D.sp(("s1464", "s1477")))
D.step("pt6", parent="pf_terminal", label="6 · Transfer the limit back to t and push forward the prior", text="Continuity and bounded convergence establish measurability and the terminal law.", spans=D.sp(("s1478", "s1498")))

D.proof("pf_equivariance", parent="r_equivariance", label="Proof of similarity equivariance", text="Compute the transformed denoiser and verify the transformed path solves the transformed ODE.", spans=D.sp("s1370"))
D.step("pe1", parent="pf_equivariance", label="1 · The transformed denoiser is gamma(O m + b)", text="Change variables in the posterior integral.", spans=D.sp(("s1371", "s1373")))
D.step("pe2", parent="pf_equivariance", label="2 · The transformed trajectory solves the transformed ODE", text="Differentiate y_t=s_t(Ox_t+alpha_t b) and match coefficients.", spans=D.sp(("s1374", "s1379")))
D.step("pe3", parent="pf_equivariance", label="3 · Pass to terminal time", text="Continuity of the schedules preserves the limit.", spans=D.sp("s1380"))

D.proof("pf_atom", parent="r_atom_absorption", label="Proof of atom absorption", text="Uniform posterior concentration maps the shrunk Voronoi boundary inward and then contracts distance to the selected atom.", spans=D.sp("s1381"))
D.step("pva1", parent="pf_atom", label="1 · Fit an interior ball inside the shrunk Voronoi cell", text="Separation determines the radius.", spans=D.sp(("s1382", "s1384")))
D.step("pva2", parent="pf_atom", label="2 · Posterior concentration maps the boundary inward", text="The sigma threshold makes the denoiser land in that ball, hence the cell is absorbing.", spans=D.sp(("s1385", "s1392")))
D.step("pva3", parent="pf_atom", label="3 · Contract distance to the selected atom", text="The discrete denoiser error is super-exponentially small in lambda.", spans=D.sp(("s1393", "s1401")))
D.proof("pf_learned_mem", parent="r_learned_mem", label="Proof of learned-denoiser memorization", text="Uniform asymptotic denoiser error preserves Voronoi absorption and convergence to the same training atom.", spans=D.sp("s1402"))
D.step("plm1", parent="pf_learned_mem", label="1 · Reparameterize the learned ODE by lambda", text="The learned dynamics retain the denoiser-minus-state form.", spans=D.sp(("s1403", "s1408")))
D.step("plm2", parent="pf_learned_mem", label="2 · Exact plus approximation error maps the boundary inward", text="Both terms vanish, so the shrunk Voronoi cell becomes absorbing.", spans=D.sp(("s1409", "s1413")))
D.step("plm3", parent="pf_learned_mem", label="3 · The absorbing trajectory converges to its atom", text="Apply the same distance differential inequality with the learned error term.", spans=D.sp(("s1414", "s1416")))
D.step("plm4", parent="pf_learned_mem", label="4 · Convergent state and denoiser imply their gap vanishes", text="A nonzero limiting derivative would contradict convergence of a coordinate.", spans=D.sp(("s1417", "s1425")))


# ---- Experiments: synthetic, CIFAR-10, and FFHQ -------------------------------
D.construct("x_syn_data", "Synthetic three-cluster dataset", "144 two-dimensional points in three unequal uniform disks; total diameter 2.623.", subtype="dataset", function="setup", spans=D.sp(("s1548", "s1556")))
D.construct("x_syn_method", "Exact-denoiser rectified-flow simulation", "Use the closed-form optimal denoiser with alpha=t, beta=1-t, start at sigma=100, and convert trajectories to sigma coordinates.", subtype="method", function="setup", spans=D.sp(("s1557", "s1560")))
D.target("qx_stages", "Do observed turning points match the predicted stage thresholds?", "Compare the mean, cluster, and atom thresholds from the theory with the actual synthetic paths.", subtype="evaluation_question", spans=D.sp(("s1561", "s1564")))
D.statement("x_initial", "Synthetic paths reach the mean before the predicted initial threshold", "Across several initializations, paths mostly move nearly linearly toward the mean before sigma_init=13; one overshoots and is later caught by a cluster.", warrant="observed", function="evidence", spans=D.sp(("s1568", "s1575")))
D.statement("x_cluster", "The predicted cluster threshold aligns with visible capture", "For the yellow cluster, sigma_cluster=0.65 falls near the point where two example paths visibly turn toward that cluster.", warrant="observed", function="evidence", spans=D.sp(("s1576", "s1582")))
D.statement("x_terminal", "Predicted atom thresholds lie inside the final attraction segments", "The two example paths converge to training atoms, and thresholds 0.007 and 0.004 occur after atom-specific attraction begins.", warrant="observed", function="evidence", spans=D.sp(("s1583", "s1590")))
D.statement("x_perturb", "Vanishing denoiser perturbations still end at training atoms", "Adding sigma-scaled Gaussian perturbations visibly bends paths, yet all tested paths converge to data atoms as the perturbation decays.", warrant="observed", function="evidence", spans=D.sp(("s1591", "s1598")))

D.construct("x_cifar", "CIFAR-10 evaluation dataset and preprocessing", "50,000 normalized 32x32 RGB training images with dataset diameter 106.8 and average norm 27.2.", subtype="dataset", function="setup", spans=D.sp(("s1599", "s1604")))
D.construct("x_cifar_models", "Empirical optimum versus pretrained EDM denoiser", "Compare the exact empirical posterior mean with a pretrained EDM denoiser under the same 18-step polynomial schedule from sigma=80 to 0.002.", subtype="baseline", function="setup", spans=D.sp(("s1605", "s1609")))
D.target("qx_cifar_mean", "Do exact and learned CIFAR denoisers show initial mean attraction?", "Measure denoiser distance to the data mean and its size relative to the trajectory direction.", subtype="evaluation_question", spans=D.sp(("s1610", "s1617")))
D.statement("x_cifar_mean", "Both CIFAR denoisers align with the mean in early steps", "Across 10,000 seeds, the relative error is tiny initially and about below 1% for the first four steps, with small variance.", warrant="observed", function="evidence", spans=D.sp(("s1618", "s1625")))
D.target("qx_cifar_mem", "Does asymptotic empirical optimality still force image memorization?", "Compare exact and heavily perturbed denoisers by visual outputs and distance to the CIFAR training set.", subtype="evaluation_question", spans=D.sp(("s1626", "s1631")))
D.construct("x_cifar_perturb", "Sigma-scaled fixed Gaussian denoiser perturbation", "Add sigma times one fixed epsilon drawn from N(0,10^2 I), preserving asymptotic optimality while heavily corrupting intermediate denoiser outputs.", subtype="method", function="setup", spans=D.sp("s1632"))
D.statement("x_cifar_mem", "Even a heavily corrupted denoiser drives paths near training images", "The exact path reaches about 0.1 training-set distance; the perturbed path reaches about 1.0 despite unrecognizable intermediate denoiser outputs, over 10,000 seeds and a coarse 18-step solver.", warrant="observed", function="evidence", spans=D.sp(("s1633", "s1646")))
D.statement("x_cifar_interpret", "The CIFAR experiment supports terminal regularization against memorization", "The authors interpret the result as evidence that asymptotic empirical optimality is enough for memorization and therefore should be regularized near terminal time.", warrant="interpreted", function="empirical_answer", spans=D.sp(("s1647", "s1648")))

D.construct("x_ffhq", "FFHQ illumination-density experiment", "Downsample 10,000 FFHQ faces to 64x64, embed them with t-SNE, and color by RGB intensity or Y-channel illumination.", subtype="dataset", function="setup", spans=D.sp(("s1649", "s1655")))
D.statement("l_ffhq_clusters", "FFHQ has density gradients, not separated theoretical clusters", "Dark and bright faces occupy dense extremes of a continuous illumination spectrum, so the exact local-cluster assumption is not met.", warrant="bounded", function="boundary", spans=D.sp(("s1656", "s1658")))
D.target("qx_ffhq", "Do FM paths gravitate toward dense illumination regions without discrete clusters?", "Test random, dark-region, and bright-region initializations in a pretrained EDM model.", subtype="evaluation_question", spans=D.sp(("s1659", "s1661")))
D.statement("x_ffhq_obs", "Initialization near an illumination region preserves that attribute", "Random starts cover the illumination spectrum, while dark and bright initializations consistently produce correspondingly illuminated faces.", warrant="observed", function="evidence", spans=D.sp(("s1662", "s1664")))


# ---- Relations ----------------------------------------------------------------
D.edge("problem_geometry", "q_geometry", "motivates")
D.edge("motivation_rigour", "q_terminal", "motivates")
D.edge("q_geometry", "c_denoiser_geometry", "answered_by")
D.edge("q_geometry", "c_three_stages", "answered_by")
D.edge("q_terminal", "c_terminal_answer", "answered_by")
D.edge("q_geometry", "qx_stages", "refines")
D.edge("q_geometry", "qx_cifar_mean", "refines")
D.edge("q_geometry", "qx_ffhq", "refines")
D.edge("q_terminal", "q_terminal_map", "refines")
D.edge("q_terminal", "q_equivariance", "refines")
D.edge("q_terminal", "q_memorization", "refines")
D.edge("q_terminal", "qx_cifar_mem", "refines")
D.edge("q_geometry", "q_dependent", "refines")
D.edge("q_terminal_map", "c_terminal_answer", "answered_by")
D.edge("q_equivariance", "intro_equivariance", "answered_by")
D.edge("q_memorization", "intro_memorization", "answered_by", basis="inferred")
D.edge("q_dependent", "a_independent_coupling", "motivates")

D.edge("d_fm_path", "m_training", "uses")
D.edge("d_sigma", "r_scaled_path", "uses")
D.edge("r_scaled_path", "r_sigma_ode", "entails", ev=["s0096"])
D.edge("r_sigma_ode", "d_denoiser_ode", "entails")
D.edge("r_scaled_path", "c_schedule_free", "supports")
D.edge("r_sigma_ode", "c_schedule_free", "supports")
D.edge("d_denoiser", "d_denoiser_ode", "uses")
D.edge("d_denoiser_role", "c_denoiser_geometry", "supports")
D.edge("d_denoiser_ode", "c_denoiser_geometry", "supports")
D.edge("d_denoiser_role", "c_denoiser_stability", "supports")
D.edge("d_denoiser_ode", "problem_moving_target", "supports")
D.edge("m_projection_test", "r_attract_formal", "uses")
D.edge("a_medial_axis", "r_attract_formal", "requires")
D.edge("r_attract_formal", "r_attract_informal", "entails")
D.edge("r_attract_informal", "c_angle_attracts", "supports")
D.edge("r_absorb", "c_denoiser_geometry", "supports")
D.edge("r_absorb_local", "c_denoiser_geometry", "supports")
D.edge("r_convex_hull", "c_convex_hull", "supports")
D.edge("c_angle_attracts", "c_denoiser_geometry", "supports")
D.edge("c_convex_hull", "c_three_stages", "supports")

D.edge("r_preterminal", "c_wellposed", "supports")
D.edge("a_schedule", "r_preterminal", "requires")
D.edge("c_wellposed", "c_preterminal_overview", "supports")
D.edge("c_wellposed", "intro_stage_results", "supports")
D.edge("r_mean", "c_mean", "supports")
D.edge("l_mean_tradeoff", "c_mean", "qualifies")
D.edge("r_cluster_denoiser", "r_cluster", "uses")
D.edge("a_local_cluster", "r_cluster_denoiser", "requires")
D.edge("a_local_cluster", "r_cluster", "requires")
D.edge("r_cluster", "c_cluster", "supports")
D.edge("r_cluster", "c_cluster_weight", "supports")
D.edge("l_cluster_scope", "c_cluster", "qualifies")
D.edge("c_mean", "c_three_stages", "supports")
D.edge("c_cluster", "c_three_stages", "supports")
D.edge("c_mean", "intro_stage_results", "supports")
D.edge("c_cluster", "intro_stage_results", "supports")
D.edge("c_cluster", "c_cluster_implication", "supports")

D.edge("r_posterior_projection", "r_denoiser_projection", "entails")
D.edge("r_denoiser_projection", "m_posterior_rate", "supports")
D.edge("a_terminal", "r_terminal", "requires")
D.edge("r_posterior_projection", "r_terminal", "uses")
D.edge("r_absorb", "r_terminal", "uses")
D.edge("r_denoiser_projection", "c_to_terminal", "supports")
D.edge("r_terminal", "c_terminal_answer", "supports")
D.edge("r_terminal_rates", "c_terminal_answer", "supports")
D.edge("r_terminal", "intro_terminal_result", "supports")
D.edge("r_terminal_rates", "intro_appendix_results", "supports")
D.edge("m_posterior_rate", "intro_appendix_results", "supports")
D.edge("r_terminal", "c_sparse_terminal_steps", "supports")
D.edge("r_distribution_rate", "q_manifold_rate", "supports")
D.edge("ex_subspace", "q_manifold_rate", "supports")
D.edge("r_terminal", "r_equivariance", "uses")
D.edge("m_schedule_transform", "r_equivariance", "uses")
D.edge("r_equivariance", "intro_equivariance", "supports")
D.edge("a_empirical_target", "r_atom_absorption", "requires")
D.edge("d_shrunk_voronoi", "r_atom_absorption", "uses")
D.edge("r_atom_absorption", "intro_memorization", "supports")
D.edge("r_atom_absorption", "c_duplicate_risk", "supports")
D.edge("r_atom_absorption", "c_terminal_training", "supports")
D.edge("d_learned_ode", "r_learned_mem", "uses")
D.edge("r_atom_absorption", "r_learned_mem", "uses")
D.edge("r_learned_mem", "intro_memorization", "supports")
D.edge("r_learned_mem", "q_memorization", "motivates")
D.edge("c_terminal_answer", "c_terminal_consequences", "supports")
D.edge("intro_equivariance", "c_terminal_consequences", "supports")
D.edge("intro_memorization", "c_terminal_consequences", "supports")
D.edge("c_denoiser_geometry", "intro_framework", "supports")
D.edge("c_preterminal_overview", "intro_framework", "supports")
D.edge("c_terminal_answer", "intro_framework", "supports")
D.edge("c_wellposed", "c_rigorous_path", "supports")
D.edge("c_terminal_answer", "c_rigorous_path", "supports")
D.edge("c_three_stages", "c_practical", "supports")
D.edge("c_terminal_answer", "c_practical", "supports")
D.edge("c_practical", "c_discussion", "supports")
D.edge("c_cluster_implication", "c_discussion", "supports")
D.edge("c_terminal_training", "c_discussion", "supports")

D.edge("x_syn_data", "x_syn_method", "uses")
D.edge("qx_stages", "x_initial", "answered_by")
D.edge("qx_stages", "x_cluster", "answered_by")
D.edge("qx_stages", "x_terminal", "answered_by")
D.edge("qx_stages", "x_perturb", "answered_by")
D.edge("r_mean", "x_initial", "uses")
D.edge("r_cluster", "x_cluster", "uses")
D.edge("r_atom_absorption", "x_terminal", "uses")
D.edge("r_learned_mem", "x_perturb", "uses")
D.edge("x_initial", "c_mean", "supports")
D.edge("x_cluster", "c_cluster", "supports")
D.edge("x_terminal", "intro_memorization", "supports")
D.edge("x_perturb", "intro_memorization", "supports")

D.edge("x_cifar", "x_cifar_models", "uses")
D.edge("qx_cifar_mean", "x_cifar_mean", "answered_by")
D.edge("x_cifar_models", "x_cifar_mean", "uses")
D.edge("x_cifar_mean", "c_mean", "supports")
D.edge("qx_cifar_mem", "x_cifar_mem", "answered_by")
D.edge("x_cifar_models", "x_cifar_perturb", "uses")
D.edge("x_cifar_perturb", "x_cifar_mem", "uses")
D.edge("x_cifar_mem", "x_cifar_interpret", "supports")
D.edge("x_cifar_interpret", "intro_memorization", "supports")

D.edge("l_ffhq_clusters", "x_ffhq_obs", "qualifies")
D.edge("qx_ffhq", "x_ffhq_obs", "answered_by")
D.edge("x_ffhq", "x_ffhq_obs", "uses")
D.edge("x_ffhq_obs", "c_cluster", "supports")

# Proof containment edges make theorem-to-proof drill-down explicit.
for proof_id, theorem_id, steps in [
    ("pf_attract", "r_attract_formal", ["pa1", "pa2", "pa3"]),
    ("pf_absorb", "r_absorb", ["pb1", "pb2", "pb3"]),
    ("pf_preterminal", "r_preterminal", ["pw1", "pw2", "pw3", "pw4", "pw5", "pw6"]),
    ("pf_mean", "r_mean", ["pm1", "pm2", "pm3", "pm4"]),
    ("pf_cluster_denoiser", "r_cluster_denoiser", ["pcd1", "pcd2", "pcd3"]),
    ("pf_cluster", "r_cluster", ["pc1", "pc2", "pc3"]),
    ("pf_projection", "r_posterior_projection", ["pp1", "pp2", "pp3", "pp4"]),
    ("pf_denoiser_projection", "r_denoiser_projection", []),
    ("pf_terminal", "r_terminal", ["pt1", "pt2", "pt3", "pt4", "pt5", "pt6"]),
    ("pf_equivariance", "r_equivariance", ["pe1", "pe2", "pe3"]),
    ("pf_atom", "r_atom_absorption", ["pva1", "pva2", "pva3"]),
    ("pf_learned_mem", "r_learned_mem", ["plm1", "plm2", "plm3", "plm4"]),
]:
    D.edge(proof_id, theorem_id, "proves")
    for step in steps:
        D.edge(step, theorem_id, "proves")
    for left, right in zip(steps, steps[1:]):
        D.edge(left, right, "entails")

report = D.build(out)
print({k: v for k, v in report.items() if k != "problems"})
if report["problems"]:
    print("PROBLEMS", report["problems"])
