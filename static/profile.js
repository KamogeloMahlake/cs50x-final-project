const userDetails = document.getElementById('user-details');
const novel = document.getElementById('novels');
const novelsButton = document.querySelector('.novels-button');
let showNovel = false;

novelsButton.addEventListener("click", async () => {
	if (showNovel === true)
	{
		novel.innerHTML = "";
		showNovel = false;
	}
	else
	{
		let response = await fetch("/profile/novels");
		let novels = await response.json()
		let html = "";

		novels.forEach(novel => {
			html += `<li class="list-group-item container">
                <div class="row">
                <h6 class="col-6">
					        <a href="/novel/${novel.name}">${novel.name}</a>
				        </h6>
                <a class="col-6" href="/profile/${novel.name}/update">
                  <button class="btn btn-primary">Update</button>
                </a>
                </div>
              </li>`;
		})
		novel.innerHTML = html;
		showNovel = true;
	}
	userDetails.classList.toggle('hidden');
	novel.classList.toggle('hidden');
	novelsButton.textContent = novelsButton.textContent === "All novels" ? "Show Profile" : "All novels";
});

